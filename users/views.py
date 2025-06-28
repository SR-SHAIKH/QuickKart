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