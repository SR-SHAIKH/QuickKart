from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .forms import ProfileUpdateForm
from .forms import CustomerProfileForm 
from shop.models import Order  
from shop.models import Wishlist  
from shop.models import CartItem

from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import RegistrationForm
from users.models import CustomUser
import random

from .forms import RiderRegistrationForm
from shop.models import PinCode
import json

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

# from cart.models import Cart  


# -------------------- Password Change View --------------------
class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('password_change_done')  # You can change this to 'profile' if you want


@login_required
def customer_profile_view(request):
    if request.user.role != 'customer':
        return redirect('home')

    orders = Order.objects.filter(customer=request.user)
    wishlist_items = Wishlist.objects.filter(user=request.user)
    cart_items = CartItem.objects.filter(user=request.user)  # ✅ CartItem, not Cart

    context = {
        'user': request.user,
        'orders': orders,
        'wishlist_items': wishlist_items,
        'cart_items': cart_items,
    }
    return render(request, 'dashboard/customer_profile.html', context)


@login_required
def customer_edit_profile(request):
    if request.user.role != 'customer':
        return redirect('home')

    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('customer_profile')
    else:
        form = CustomerProfileForm(instance=request.user)

    return render(request, 'dashboard/customer_edit_profile.html', {'form': form})


@login_required
def owner_profile_view(request):
    if request.user.role != 'shop_owner':
        return redirect('home')
    return render(request, 'dashboard/owner_profile.html', {'user': request.user})

@login_required
def customer_edit_profile(request):
    if request.user.role != 'customer':
        return redirect('home')
    
    form = CustomerProfileForm(request.POST or None, request.FILES or None, instance=request.user)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('customer_profile')
    
    return render(request, 'dashboard/customer_edit_profile.html', {'form': form})


@login_required
def owner_edit_profile(request):
    if request.user.role != 'shop_owner':
        return redirect('home')
    form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('owner_profile')
    return render(request, 'dashboard/owner_edit_profile.html', {'form': form})

@login_required
def owner_profile_view(request):
    if request.user.role != 'shop_owner':
        return redirect('home')

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('owner_profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'dashboard/owner_profile.html', {'form': form})

def register(request):
    role = request.GET.get('role')
    if role == 'shop_owner':
        request.session['register_role'] = 'shop_owner'
        return redirect('register_owner_step1')  # You will define this in shop/views.py
    elif role == 'customer':
        request.session['register_role'] = 'customer'
        return redirect('customer_register_otp')
    else:
        return redirect('home')


def customer_register_otp(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            request.session['temp_user_data'] = form.cleaned_data
            otp = str(random.randint(100000, 999999))
            request.session['otp'] = otp

            # Send OTP via email
            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return redirect('verify_customer_otp')
    else:
        form = RegistrationForm()
    return render(request, 'users/customer_register.html', {'form': form})


def verify_customer_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if entered_otp == request.session.get('otp'):
            data = request.session.get('temp_user_data')
            if data:
                # Save the user only after successful OTP
                user = CustomUser.objects.create_user(
                    username=data['username'],
                    email=data['email'],
                    password=data['password'],
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', ''),
                    role='customer',
                )
                user.save()

                # Clear session
                request.session.pop('otp')
                request.session.pop('temp_user_data')
                messages.success(request, 'Registration successful. Please log in.')
                return redirect('login')
        else:
            messages.error(request, 'Invalid OTP.')
    return render(request, 'users/verify_otp.html')

def rider_register(request):
    if request.method == 'POST':
        form = RiderRegistrationForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            rider = form.save(commit=False)
            # Set any additional fields if needed
            rider.save()
            # Get selected pincode IDs from hidden inputs (JS)
            pincode_ids = request.POST.getlist('delivery_pincodes')
            rider.delivery_pincodes.set(pincode_ids)
            # You can add messages, redirect, etc. here
            return redirect('login')  # Or wherever you want
    else:
        form = RiderRegistrationForm()
    all_pincodes = PinCode.objects.all()
    all_pincodes_json = json.dumps([
        {"id": p.id, "code": p.code, "area": getattr(p, "area_name", "")} for p in all_pincodes
    ])
    return render(request, 'users/rider_register.html', {
        'form': form,
        'all_pincodes_json': all_pincodes_json,
    })

def rider_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'rider':
        return redirect('login')
    # Handle On Duty toggle
    if request.method == 'POST' and 'on_duty_toggle' in request.POST:
        request.user.on_duty = not request.user.on_duty
        request.user.save()
        messages.success(request, f"You are now {'On Duty' if request.user.on_duty else 'Off Duty'}.")
        return redirect('rider_dashboard')

    # Handle Accept/Decline/Delivered actions
    if request.method == 'POST' and 'order_id' in request.POST:
        order_id = request.POST.get('order_id')
        action = request.POST.get('action')
        order = Order.objects.get(id=order_id, delivery_rider=request.user)
        if action == 'accept' and order.rider_status == 'pending' and order.status == 'shipped':
            order.rider_status = 'accepted'
            order.status = 'out_for_delivery'
            order.save()
            messages.success(request, f'Order #{order.id} accepted and marked as Out for Delivery.')
            return redirect('rider_dashboard')
        elif action == 'reject' and order.rider_status == 'pending' and order.status == 'shipped':
            order.rider_status = 'declined'
            backups = list(order.backup_riders.all())
            if backups:
                next_rider = backups[0]
                order.delivery_rider = next_rider
                order.backup_riders.remove(next_rider)
                order.rider_status = 'pending'
                order.save()
                messages.info(request, f'Order #{order.id} assigned to next backup rider.')
            else:
                order.delivery_rider = None
                order.status = 'confirmed'
                order.save()
                messages.warning(request, f'All backup riders rejected Order #{order.id}. Please reassign.')
            return redirect('rider_dashboard')
        elif action == 'mark_delivered' and order.rider_status == 'accepted' and order.status == 'out_for_delivery':
            order.status = 'delivered'
            order.save()
            messages.success(request, f'Order #{order.id} marked as Delivered!')
            return redirect('rider_dashboard')

    assigned_deliveries = Order.objects.filter(delivery_rider=request.user).order_by('-order_date')
    return render(request, 'users/rider_dashboard.html', {
        'assigned_deliveries': assigned_deliveries,
        'rider': request.user,
    })

def login_view(request):
    error = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'rider':
                return redirect('rider_dashboard')
            elif user.role == 'shop_owner':
                return redirect('owner_profile')  # or your shop owner dashboard
            else:
                return redirect('customer_profile')  # or your customer dashboard
        else:
            error = 'Invalid email or password.'
    return render(request, 'users/login.html', {'error': error})