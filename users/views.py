from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .forms import ProfileUpdateForm
from .forms import CustomerProfileForm 
from shop.models import Order, Payment
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
from django.urls import reverse
from django.http import HttpResponseRedirect

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
                
                # Auto login after successful registration
                login(request, user)
                messages.success(request, 'Registration successful! Welcome to QuickKart.')
                return redirect('home')
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
            
            # Auto login after successful registration
            login(request, rider)
            messages.success(request, 'Registration successful! Welcome to QuickKart.')
            return redirect('rider_dashboard')
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

@login_required
def rider_dashboard(request):
    
    if request.user.role != 'rider':
        return redirect('home')

    # --- Filter & Sort Logic ---
    status_filter = request.GET.get('status_filter', 'all')
    sort_order = request.GET.get('sort_order', 'newest')
    params = f'?status_filter={status_filter}&sort_order={sort_order}'

    # Handle POST for toggling duty status
    if request.method == 'POST' and 'toggle_duty' in request.POST:
        request.user.on_duty = not request.user.on_duty
        request.user.save()
        messages.info(request, f'You are now {"On Duty" if request.user.on_duty else "Off Duty"}.')
        return HttpResponseRedirect(reverse('rider_dashboard') + params)

    orders = Order.objects.filter(delivery_rider=request.user).prefetch_related('items__product', 'customer')
    if status_filter != 'all':
        if status_filter == 'declined':
            orders = orders.filter(rider_status='declined')
        elif status_filter == 'delivered':
            orders = orders.filter(status='delivered')
        elif status_filter == 'pending':
            orders = orders.filter(rider_status='accepted').exclude(status='delivered')
    if sort_order == 'newest':
        orders = orders.order_by('-order_date')
    else:
        orders = orders.order_by('order_date')

    # Stats for Earnings & Stats
    all_assigned_orders = Order.objects.filter(delivery_rider=request.user)
    total_assigned = all_assigned_orders.count()
    total_rejected = all_assigned_orders.filter(rider_status='declined').count()
    total_selected = all_assigned_orders.filter(rider_status='accepted').count()
    total_delivered = all_assigned_orders.filter(status='delivered').count()
    total_pending = all_assigned_orders.filter(rider_status='accepted', status='out_for_delivery').count()

    # Handle POST for status update or rejection
    if request.method == 'POST' and 'order_id' in request.POST:
        order_id = request.POST.get('order_id')
        action = request.POST.get('action')
        order = Order.objects.get(id=order_id, delivery_rider=request.user)
        if action == 'reject':
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
            return HttpResponseRedirect(reverse('rider_dashboard') + params)
        elif action == 'accept' and order.rider_status == 'pending' and order.status == 'shipped':
            order.rider_status = 'accepted'
            order.status = 'out_for_delivery'
            order.save()
            messages.success(request, f'Order #{order.id} accepted and marked as Out for Delivery.')
            return HttpResponseRedirect(reverse('rider_dashboard') + params)
        elif action == 'mark_delivered' and order.rider_status == 'accepted' and order.status == 'out_for_delivery':
            order.status = 'delivered'
            order.save()
            try:
                payment = Payment.objects.get(order=order, payment_method='cod')
                payment.payment_status = 'completed'
                payment.save()
                if payment.invoice:
                    payment.invoice.payment_status = 'paid'
                    payment.invoice.save()
                messages.success(request, f'Order #{order.id} delivered! COD payment marked as completed.')
            except Payment.DoesNotExist:
                messages.success(request, f'Order #{order.id} marked as Delivered!')
            return HttpResponseRedirect(reverse('rider_dashboard') + params)
    return render(request, 'users/rider_dashboard.html', {
        'assigned_deliveries': orders,
        'rider': request.user,
        'on_duty': request.user.on_duty,
        'total_assigned': total_assigned,
        'total_rejected': total_rejected,
        'total_selected': total_selected,
        'total_delivered': total_delivered,
        'total_pending': total_pending,
        'status_filter': status_filter,
        'sort_order': sort_order,
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
                return redirect('shop_owner_dashboard')
            else:
                return redirect('home')  # Customer goes to home page
        else:
            error = 'Invalid email or password.'
    return render(request, 'users/login.html', {'error': error})

from .forms import RiderEditProfileForm

@login_required
def rider_edit_profile(request):
    if request.user.role != 'rider':
        return redirect('home')
    if request.method == 'POST':
        form = RiderEditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('rider_dashboard')
    else:
        form = RiderEditProfileForm(instance=request.user)
    return render(request, 'users/rider_edit_profile.html', {'form': form})