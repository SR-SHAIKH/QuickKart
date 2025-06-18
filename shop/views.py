from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
import random

from .forms import RegistrationForm, ProductForm
from .models import CustomUser, Product, CartItem

# Home View
def home(request):
    return render(request, 'home.html')

# OTP Utilities
def generate_otp():
    return random.randint(100000, 999999)

def send_otp_email(email, otp):
    send_mail(
        'Your OTP Code',
        f'Your OTP code is {otp}',
        'shaikhsohel.edu@gmail.com',
        [email],
        fail_silently=False,
    )

# 1. Registration View
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            otp = generate_otp()
            request.session['registration_data'] = form.cleaned_data
            request.session['otp'] = str(otp)
            send_otp_email(form.cleaned_data['email'], otp)
            return redirect('verify_otp')
    else:
        form = RegistrationForm()
    return render(request, 'shop/register.html', {'form': form})

# 2. OTP Verification View
from .models import CustomUser

def verify_otp(request):
    error = None
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        if entered_otp == session_otp:
            data = request.session.get('registration_data')
            if data:
                form = RegistrationForm(data)
                if form.is_valid():
                    user = form.save()
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')  # 🛠️ Add backend here
                    del request.session['registration_data']
                    del request.session['otp']
                    if user.role == 'shop_owner':
                        return redirect('shop_dashboard')
                    else:
                        return redirect('customer_dashboard')
        else:
            #  If OTP is wrong, try to delete the user by email
            data = request.session.get('registration_data')
            if data:
                try:
                    user = CustomUser.objects.get(email=data['email'])
                    user.delete()
                except CustomUser.DoesNotExist:
                    pass
            error = 'Invalid OTP. Please try again.'
    return render(request, 'shop/verify_otp.html', {'error': error})

# 3. Shop Owner Views
@login_required
def shop_dashboard(request):
    if request.user.role != 'shop_owner':
        return redirect('home')
    products = Product.objects.filter(shop_owner=request.user)
    return render(request, 'shop/shop_dashboard.html', {'products': products})

@login_required
def create_product(request):
    if request.user.role != 'shop_owner':
        return redirect('home')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.shop_owner = request.user
            product.save()
            return redirect('shop_dashboard')
    else:
        form = ProductForm()
    return render(request, 'products/create_product.html', {'form': form})

@login_required
def edit_product(request, product_id):
    product = Product.objects.get(id=product_id, shop_owner=request.user)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('shop_dashboard')
    return render(request, 'products/edit_product.html', {'form': form, 'product': product})

@login_required
def delete_product(request, product_id):
    product = Product.objects.get(id=product_id, shop_owner=request.user)
    if request.method == 'POST':
        product.delete()
        return redirect('shop_dashboard')
    return render(request, 'products/delete_product.html', {'product': product})

# 4. Customer Views
@login_required
def product_list(request):
    if request.user.role != 'customer':
        return redirect('home')
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    for item in cart_items:
        item.total_price = item.product.price * item.quantity
    total = sum(item.total_price for item in cart_items)
    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total': total})

# Login View
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'shop_owner':
                return redirect('shop_dashboard')
            elif user.role == 'customer':
                return redirect('customer_dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'shop/login.html')

# ✅ Logout View
def logout_view(request):
    logout(request)
    return redirect('home')

# 5. Customer Dashboard View
@login_required
def customer_dashboard(request):
    if request.user.role != 'customer':
        return redirect('home')
    return render(request, 'shop/customer_dashboard.html')


# Add to Cart View
# Add to Cart View
@login_required
def add_to_cart(request, product_id):
    if request.user.role != 'customer':
        return redirect('home')

    product = Product.objects.get(id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart_view')

from django.shortcuts import get_object_or_404

@login_required
def remove_from_cart(request, item_id):
    if request.user.role != 'customer':
        return redirect('home')

    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart_view')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def checkout(request):
    # Example placeholder logic; customize as needed
    if request.method == 'POST':
        # process payment and order creation logic here
        return redirect('order_success')
    # Show checkout page with cart details
    return render(request, 'checkout.html')




