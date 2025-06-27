from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.template.loader import get_template
from django.utils.timezone import now
from django.http import JsonResponse

from .forms import RegistrationForm, ProductForm, CustomerProfileForm
from .models import (
    Product, CartItem, Order, OrderItem,
    Wishlist, Category, PinCode, Brand, Shop
)
from users.models import CustomUser

import random

# --------------------- GENERAL ---------------------
from django.db.models import Q  # For flexible filtering

def home(request):
    query = request.GET.get('q', '')
    selected_pincode = request.session.get('selected_pincode')

    categories = Category.objects.all()
    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    wishlist_products = []
    if request.user.is_authenticated and request.user.role == 'customer':
        wishlist_products = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)

    shops_in_area = Shop.objects.all()
    if selected_pincode:
        shops_in_area = Shop.objects.filter(delivery_pincodes__code=selected_pincode).distinct()
        products = products.filter(shop__in=shops_in_area)

    bestselling_products = products.order_by('-sales_count')[:10] if selected_pincode else products[:10]

    return render(request, 'shop/home.html', {
        'products': products,
        'bestselling_products': bestselling_products,
        'categories': categories,
        'shops_in_area': shops_in_area,
        'wishlist_products': wishlist_products,
        'query': query,
    })


# --------------------- OTP UTILS ---------------------
def generate_otp():
    return random.randint(100000, 999999)

def send_otp_email(email, otp):
    send_mail(
        'Your OTP Code',
        f'Your OTP code is {otp}',
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )


# --------------------- AUTH ---------------------
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


def verify_otp(request):
    error = None
    registration_data = request.session.get('registration_data')
    if not registration_data:
        messages.error(request, "Session expired or invalid access. Please register again.")
        return redirect('register')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')

        if entered_otp == session_otp:
            form = RegistrationForm(registration_data)
            if form.is_valid():
                user = form.save()
                user.username = user.email.split('@')[0]
                user.first_name = registration_data.get('first_name', '')
                user.last_name = registration_data.get('last_name', '')
                user.save()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                request.session.pop('registration_data', None)
                request.session.pop('otp', None)
                return redirect('shop_owner_dashboard' if user.role == 'shop_owner' else 'customer_dashboard')
        else:
            try:
                CustomUser.objects.get(email=registration_data['email']).delete()
            except CustomUser.DoesNotExist:
                pass
            error = 'Invalid OTP. Please try again.'

    return render(request, 'shop/verify_otp.html', {'error': error})


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            if user.role == 'shop_owner':
                return redirect('shop_owner_dashboard')
            else:
                return redirect('home')  # ✅ Redirect customers to home
        messages.error(request, 'Invalid email or password.')
    return render(request, 'shop/login.html')


# --------------------- DASHBOARDS ---------------------
@login_required
def customer_dashboard(request):
    if request.user.role != 'customer':
        return redirect('home')
    return render(request, 'dashboard/customer_dashboard.html')


def is_shop_owner(user):
    return user.role == 'shop_owner'

@login_required
@user_passes_test(lambda u: u.role == 'shop_owner')
def shop_owner_dashboard(request):
    products = Product.objects.filter(shop_owner=request.user)
    return render(request, 'products/owner_products.html', {
        'products': products,
        'now': now()
    })

@login_required
@user_passes_test(is_shop_owner)
def shop_owner_products(request):
    products = Product.objects.filter(shop_owner=request.user)
    return render(request, 'products/owner_products.html', {'products': products})


@login_required
@user_passes_test(lambda u: u.role == 'shop_owner')
def shop_owner_orders(request):
    orders = Order.objects.filter(
        items__product__shop_owner=request.user
    ).prefetch_related('items__product', 'customer').distinct()

    return render(request, 'products/owner_orders.html', {'orders': orders})

# --------------------- SHOP OWNER FEATURES ---------------------
@login_required
@user_passes_test(is_shop_owner)
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.shop_owner = request.user
            product.save()
            return redirect('shop_owner_dashboard')
    else:
        form = ProductForm()
    return render(request, 'products/create_product.html', {'form': form})


@login_required
@user_passes_test(is_shop_owner)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, shop_owner=request.user)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('shop_owner_dashboard')  # ✅ Only the name, no extra dict
    return render(request, 'products/edit_product.html', {'form': form, 'product': product})


@login_required
@user_passes_test(is_shop_owner)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, shop_owner=request.user)
    if request.method == 'POST':
        product.delete()
        return redirect('shop_owner_dashboard')
    return render(request, 'products/delete_product.html', {'product': product})


# --------------------- CUSTOMER FEATURES ---------------------
# @login_required
# def product_list(request):
#     if request.user.role != 'customer':
#         return redirect('home')
#     products = Product.objects.all()
#     return render(request, 'products/product_list.html', {'products': products})


@login_required
def cart_view(request):
    if request.user.role != 'customer':
        return redirect('home')
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    for item in cart_items:
        item.total_price = item.product.price * item.quantity
    total = sum(item.total_price for item in cart_items)
    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total': total})


@login_required
def add_to_cart(request, product_id):
    if request.user.role != 'customer':
        return redirect('home')
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')


@login_required
def remove_from_cart(request, item_id):
    if request.user.role != 'customer':
        return redirect('home')
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart')


@login_required
def checkout(request):
    if request.user.role != 'customer':
        return redirect('home')

    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart')

    total = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        # Create the Order Change user to customer
        order = Order.objects.create(
            customer=request.user,
            total_amount=total
        )

        # Create OrderItems from CartItems
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # Clear the cart
        cart_items.delete()

        return redirect('order_success')

    return render(request, 'shop/checkout.html', {
        'cart_items': cart_items,
        'total': total,
    })


@login_required
def my_orders(request):
    if request.user.role != 'customer':
        return redirect('home')

    orders = Order.objects.filter(customer=request.user).prefetch_related('items__product')
    return render(request, 'shop/my_orders.html', {'orders': orders})
    

# --------------------- PROFILE ---------------------
@login_required
def customer_profile_view(request):
    if request.user.role != 'customer':
        return redirect('home')

    orders = Order.objects.filter(customer=request.user)
    wishlist_items = Wishlist.objects.filter(user=request.user)
    cart_items = CartItem.objects.filter(user=request.user)  # ✅ correct model

    context = {
        'user': request.user,
        'orders': orders,
        'wishlist_items': wishlist_items,
        'cart_items': cart_items,
    }
    return render(request, 'dashboard/customer_profile.html', context)
# --------------------- ORDER SUCCESS ---------------------
@login_required
def order_success(request):
    return render(request, 'shop/order_success.html')

def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # ✅ Store this product in session or direct user to checkout
    # This is up to your logic
    request.session['buy_now_product_id'] = product.id
    
    return redirect('checkout')  # or your custom checkout route


@login_required
def add_to_wishlist(request, product_id):
    product = Product.objects.get(pk=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('home')

@login_required
def wishlist_page(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'shop/wishlist.html', {'wishlist_items': wishlist_items})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    suggested_products = Product.objects.exclude(pk=pk)[:5]

    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(user=request.user, product=product).exists()

    return render(request, 'shop/product_detail.html', {
        'product': product,
        'suggested_products': suggested_products,
        'is_wishlisted': is_wishlisted
    })


@login_required
def toggle_wishlist_ajax(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        product = get_object_or_404(Product, id=product_id)
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

        if not created:
            wishlist_item.delete()
            return JsonResponse({"status": "removed"})
        return JsonResponse({"status": "added"})

    return JsonResponse({"error": "Invalid request"}, status=400)

# @login_required
def edit_customer_profile(request):
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
def logout_view(request):
    logout(request)
    return redirect('login')

def search_view(request):
    query = request.GET.get('q', '')
    # your product filtering logic here
    results = Product.objects.filter(name__icontains=query)
    return render(request, 'shop/search_results.html', {'results': results, 'query': query})

@login_required
def order_history(request):
    orders = Order.objects.filter(customer=request.user)
    return render(request, 'shop/my_orders.html', {'orders': orders})
def products_by_category(request, category_id):
    products = Product.objects.filter(category_id=category_id)
    categories = Category.objects.all()
    wishlist_products = []

    if request.user.is_authenticated and request.user.role == 'customer':
        wishlist_products = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)

    return render(request, 'shop/home.html', {
        'products': products,
        'categories': categories,
        'wishlist_products': wishlist_products,
    })
