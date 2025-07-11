from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.template.loader import get_template
from django.utils.timezone import now
from django.http import JsonResponse
from shop.form_parts.owner_step1_form import OwnerPersonalForm
from shop.form_parts.owner_step2_form import ShopForm
from shop.form_parts.owner_step3_form import ShopBankForm
from shop.form_parts.registration_form import RegistrationForm
from shop.form_parts.product_form import ProductForm
from shop.form_parts.customer_profile_form import CustomerProfileForm
from .forms import EditShopProfileForm
# from django.contrib.auth.decorators import login_required
# from django.db.models import Sum
from .models import Shop, PinCode
import json
from shop.forms import ShopBankForm
from .models import (
    Product, CartItem, Order, OrderItem,
    Wishlist, Category, PinCode, Brand, Shop
)
from users.models import CustomUser

import random

# --------------------- GENERAL ---------------------
from django.db.models import Q  # For flexible filtering

from django.db.models import Q
from .models import Category, Product, Shop, Wishlist, PinCode

from django.shortcuts import render
from django.db.models import Q
from shop.models import Product, Category, Shop, PinCode, Wishlist

def home(request):
    print("🔥 Home view called")

    # GET se pincode mila? to session me save karo
    if request.GET.get('pincode'):
        request.session['selected_pincode'] = request.GET.get('pincode')

    # PinCode: pehle session se lo (GET se agar hai to upar hi save ho chuka)
    selected_pincode = request.session.get('selected_pincode')

    query = request.GET.get('q', '').strip()

    categories = Category.objects.all()
    products = Product.objects.none()
    shops_in_area = Shop.objects.none()
    wishlist_products = []

    if selected_pincode:
        print("🧠 Selected PinCode:", selected_pincode)

        try:
            pin_obj = PinCode.objects.get(code=selected_pincode)
            print("✅ PinCode object:", pin_obj)

            shops_in_area = Shop.objects.filter(delivery_pincodes=pin_obj).distinct()
            print("🏪 Shops in Area:", shops_in_area)

            products = Product.objects.filter(shop__in=shops_in_area, is_active=True).distinct()
            print("📦 Filtered Products:", products)

            if query:
                products = products.filter(
                    Q(name__icontains=query) | Q(description__icontains=query)
                )

            if request.user.is_authenticated and getattr(request.user, 'role', None) == 'customer':
                wishlist_products = Wishlist.objects.filter(
                    user=request.user
                ).values_list('product_id', flat=True)

        except PinCode.DoesNotExist:
            print("❌ PinCode not found!")

    bestselling_products = products.order_by('-stock')[:10] if products.exists() else []

    context = {
        'products': products,
        'bestselling_products': bestselling_products,
        'categories': categories,
        'shops_in_area': shops_in_area,
        'wishlist_products': wishlist_products,
        'query': query,
    }

    return render(request, 'shop/home.html', context)


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
    role_from_get = request.GET.get("role")

    # 🔁 Redirect to role selection if no role and not POST
    if not role_from_get and request.method != 'POST':
        return redirect('select_role')  # 👈 You must define this route and view

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            email = form.cleaned_data['email']

            # Email already registered
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, "This email is already registered.")
                return render(request, 'shop/register.html', {'form': form})

            # 🔁 Shop Owner ➤ Go to Step 1
            if role == 'shop_owner':
                request.session['owner_user_data'] = {
                    'first_name': form.cleaned_data.get('first_name', ''),
                    'last_name': form.cleaned_data.get('last_name', ''),
                    'username': email.split('@')[0],  # fallback username
                    'email': email,
                    'password': form.cleaned_data['password1'],
                }
                return redirect('register_owner_step1')

            # ✅ Customer ➤ OTP verification
            otp = generate_otp()
            request.session['registration_data'] = form.cleaned_data
            request.session['otp'] = str(otp)

            try:
                send_otp_email(email, otp)
            except Exception as e:
                messages.error(request, "Failed to send OTP. Try again later.")
                return render(request, 'shop/register.html', {'form': form})

            return redirect('verify_otp')

    else:
        # Pre-fill role in form from query param
        form = RegistrationForm(initial={'role': role_from_get})

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
    return render(request, 'dashboard/shop_owner_dashboard.html', {
        'products': products,
        # Include extra context if needed like total_orders, monthly_revenue, etc.
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

    # For each order, find eligible riders (by pin code)
    eligible_riders_map = {}
    for order in orders:
        import re
        match = re.search(r'(\d{6})', order.delivery_address)
        pin_code = match.group(1) if match else None
        print(f"Order {order.id} delivery_address: {order.delivery_address}, extracted pin_code: {pin_code}")
        if pin_code:
            eligible_riders = CustomUser.objects.filter(role='rider', on_duty=True, delivery_pincodes__code=pin_code).distinct()
            print(f"Eligible riders for pincode {pin_code}: {[r.email for r in eligible_riders]}")
        else:
            eligible_riders = CustomUser.objects.none()
        eligible_riders_map[order.id] = eligible_riders

    manual_status_choices = [
        ('customer_pickup', 'Customer Pickup'),
        ('cancelled', 'Cancelled'),
        ('owner_delivery', 'Owner Delivery'),
    ]

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        action = request.POST.get('action')
        rider_ids = request.POST.getlist('rider_ids')
        manual_status = request.POST.get('manual_status')
        order = Order.objects.get(id=order_id)
        if action == 'confirm' and order.status == 'pending' and order.items.first().product.shop_owner == request.user:
            order.status = 'confirmed'
            order.save()
            messages.success(request, f'Order #{order.id} confirmed!')
            return redirect('shop_owner_orders')
        if order.status == 'confirmed' and order.items.first().product.shop_owner == request.user:
            if rider_ids:
                order.delivery_rider_id = rider_ids[0]
                order.status = 'shipped'
                order.save()
                order.backup_riders.set(rider_ids[1:])
                messages.success(request, f'Order #{order.id} assigned to rider(s) successfully!')
            elif manual_status:
                order.status = manual_status
                order.save()
                messages.info(request, f'Order #{order.id} status updated to {order.get_status_display()}.')
            return redirect('shop_owner_orders')
        if action == 'mark_delivered' and order.status in ['shipped', 'out_for_delivery']:
            order.status = 'delivered'
            order.save()
            messages.success(request, f'Order #{order.id} marked as delivered!')
            return redirect('shop_owner_orders')
        return redirect('shop_owner_orders')

    return render(request, 'products/owner_orders.html', {'orders': orders, 'eligible_riders_map': eligible_riders_map, 'manual_status_choices': manual_status_choices})

# --------------------- SHOP OWNER FEATURES ---------------------
@login_required
@user_passes_test(lambda u: u.role == 'shop_owner')
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            # ✅ Assign the shop of the logged-in shop owner
            product.shop = request.user.shop  # make sure `OneToOneField` is set in Shop model
            product.shop_owner = request.user
            product.save()
            return redirect('shop_owner_products')
    else:
        form = ProductForm()
    return render(request, 'shop/create_product.html', {'form': form})


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
    product = get_object_or_404(Product, id=product_id)

    # 🔐 Ensure only the owner can delete
    if product.shop.shop_owner != request.user:
        return HttpResponseForbidden("You are not authorized to delete this product.")

    if request.method == 'POST':
        product.delete()
        return redirect('dashboard_owner')


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
        # Get the shop from the first cart item
        first_item = cart_items.first()
        shop = first_item.product.shop if first_item else None
        shop_pincode = None
        if shop and shop.delivery_pincodes.exists():
            shop_pincode = shop.delivery_pincodes.first().code

        # Build the delivery address
        shipping_address = request.session.get('shipping_address')
        if shipping_address:
            # Compose address string from session dict
            address_str = f"{shipping_address.get('address_line1', '')}, {shipping_address.get('address_line2', '')}, {shipping_address.get('city', '')}, {shipping_address.get('state', '')}, {shipping_address.get('country', '')} - {shipping_address.get('pin_code', '')}"
        else:
            # Fallback to user profile address
            address_str = f"{request.user.address_line1}, {request.user.address_line2}, {request.user.city}, {request.user.state}, {request.user.country} - {request.user.pin_code}"

        # Ensure the shop's pincode is in the address
        if shop_pincode and shop_pincode not in address_str:
            address_str = address_str.strip() + f" - {shop_pincode}"

        order = Order.objects.create(
            customer=request.user,
            delivery_address=address_str,
            phone=request.user.phone,
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
    request.session['buy_now_product_id'] = product.id
    return redirect('buy_now_checkout')

@login_required
def buy_now_checkout(request):
    product_id = request.session.get('buy_now_product_id')
    if not product_id:
        return redirect('home')
    product = get_object_or_404(Product, id=product_id)
    quantity = 1
    total = product.price * quantity

    # Always ensure shipping address is in session
    shipping_address = request.session.get('shipping_address')
    if not shipping_address or not shipping_address.get('address_line1') or not shipping_address.get('pin_code'):
        # Save user profile address to session if not present
        if request.user.address_line1 and request.user.pin_code:
            request.session['shipping_address'] = {
                'address_line1': request.user.address_line1,
                'address_line2': request.user.address_line2,
                'city': request.user.city,
                'state': request.user.state,
                'country': request.user.country,
                'pin_code': request.user.pin_code,
            }
            shipping_address = request.session['shipping_address']
        else:
            messages.warning(request, "No shipping address set. Please add your shipping address before placing the order.")
            return redirect('shipping_address_update')

    address_str = f"{shipping_address.get('address_line1', '')}, {shipping_address.get('address_line2', '')}, {shipping_address.get('city', '')}, {shipping_address.get('state', '')}, {shipping_address.get('country', '')} - {shipping_address.get('pin_code', '')}"

    if request.method == 'POST':
        order = Order.objects.create(
            customer=request.user,
            delivery_address=address_str,
            phone=request.user.phone,
            total_amount=total,
            status='pending',
        )
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price
        )
        request.session.pop('buy_now_product_id', None)
        return redirect('order_success')

    return render(request, 'shop/checkout.html', {
        'buy_now_product': product,
        'cart_items': None,
        'total': total,
        'is_buy_now': True,
    })


@login_required
def add_to_wishlist(request, product_id):
    product = Product.objects.get(pk=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('home')

@login_required
def wishlist_page(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'shop/wishlist.html', {'wishlist_items': wishlist_items})

from django.http import HttpResponseForbidden

def product_detail(request, pk):
    # Block shop owners
    if request.user.is_authenticated and hasattr(request.user, 'shop'):
        return HttpResponseForbidden("Access Denied. Shop owners cannot view this page.")

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
def owner_product_detail(request, pk):
    user = request.user

    # Check if this user is a shop owner
    try:
        shop = user.shop  # This confirms shop owner identity
    except Shop.DoesNotExist:
        return HttpResponseForbidden("Access Denied. Only shop owners can view this page.")

    # FIX: Use user (not shop) for querying Product
    product = get_object_or_404(Product, pk=pk, shop_owner=user)

    total_orders = OrderItem.objects.filter(product=product).count()
    total_revenue = OrderItem.objects.filter(product=product).aggregate(Sum('price'))['price__sum'] or 0

    return render(request, 'shop/owner_product_detail.html', {
        'product': product,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
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
    selected_pincode = request.session.get('selected_pincode')
    categories = Category.objects.all()
    wishlist_products = []

    products = Product.objects.filter(category_id=category_id, is_active=True)

    if selected_pincode:
        shops = Shop.objects.filter(delivery_pincodes__code=selected_pincode).distinct()
        products = products.filter(shop__in=shops)

    if request.user.is_authenticated and request.user.role == 'customer':
        wishlist_products = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)

    return render(request, 'shop/home.html', {
        'products': products,
        'categories': categories,
        'wishlist_products': wishlist_products,
    })
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password

import random
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

def register_owner_step1(request):
    if request.method == 'POST':
        form = OwnerPersonalForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            otp = random.randint(100000, 999999)

            # Save user data and OTP in session
            request.session['owner_user_data'] = {
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'username': form.cleaned_data['username'],
                'email': email,
                'password': make_password(form.cleaned_data['password']),
                'gender': form.cleaned_data.get('gender', ''),
                'date_of_birth': str(form.cleaned_data.get('date_of_birth'))  # convert to string to store in session
            }

            request.session['otp'] = str(otp)

            # Send OTP via email
            subject = 'Your OTP Code for Shop Owner Registration'
            message = f'Hello {form.cleaned_data["first_name"]},\n\nYour OTP code is: {otp}'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]

            try:
                send_mail(subject, message, from_email, recipient_list)
                messages.success(request, 'OTP sent to your email.')
            except Exception as e:
                messages.error(request, f'Error sending OTP: {e}')
                return redirect('register_owner_step1')

            return redirect('verify_owner_otp')  # 👈 Make sure this route/view exists
    else:
        form = OwnerPersonalForm()

    return render(request, 'shop/register_owner_step1.html', {'form': form})



from shop.models import Shop

from datetime import time

from datetime import time

def register_owner_step2(request):
    if 'owner_user_data' not in request.session:
        return redirect('register_owner_step1')

    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES)
        if form.is_valid():
            shop_data = form.cleaned_data.copy()

            # Convert time fields to string
            for key in ['opening_time', 'closing_time']:
                if key in shop_data and isinstance(shop_data[key], time):
                    shop_data[key] = shop_data[key].strftime('%H:%M:%S')

            # Extract delivery pin IDs
            delivery_pincodes = shop_data.pop('delivery_pincodes', [])
            request.session['delivery_pincodes'] = [p.id for p in delivery_pincodes]  # ✅ Convert to list of IDs

            # Remove file objects (handled separately)
            shop_data.pop('shop_logo', None)
            shop_data.pop('ownership_proof', None)

            request.session['owner_shop_data'] = shop_data
            request.session['shop_logo_file'] = request.FILES.get('shop_logo').name
            request.session['ownership_file'] = request.FILES.get('ownership_proof').name
            import base64

            request.session['shop_logo'] = base64.b64encode(request.FILES['shop_logo'].read()).decode('utf-8')
            request.session['ownership_proof'] = base64.b64encode(request.FILES['ownership_proof'].read()).decode('utf-8')

            return redirect('register_owner_step3')
    else:
        form = ShopForm()

        all_pincodes = PinCode.objects.all()
        all_pincodes_json = json.dumps([
        {"id": p.id, "code": p.code, "area": p.area_name} for p in all_pincodes
    ])

    return render(request, 'shop/register_owner_step2.html', {
        'form': form,
        'all_pincodes_json': all_pincodes_json
    })


from shop.models import ShopBankInfo, PinCode
from django.db import transaction

from datetime import datetime  # ✅ Needed for parsing string to time

from django.core.files.base import ContentFile
import base64

def register_owner_step3(request):
    if 'owner_user_data' not in request.session or 'owner_shop_data' not in request.session:
        return redirect('register_owner_step1')

    if request.method == 'POST':
        form = ShopBankForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # ✅ Step 1: Create the user
                    user_data = request.session['owner_user_data']
                    if 'date_of_birth' in user_data:
                        try:
                            user_data['date_of_birth'] = datetime.strptime(user_data['date_of_birth'], "%Y-%m-%d").date()
                        except:
                            user_data['date_of_birth'] = None

                    user = CustomUser.objects.create(
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        username=user_data['username'],
                        email=user_data['email'],
                        password=user_data['password'],
                        gender=user_data.get('gender', ''),
                        date_of_birth=user_data.get('date_of_birth'),
                        role='shop_owner'
                    )

                    # ✅ Step 2: Prepare shop data
                    shop_data = request.session['owner_shop_data']
                    shop_data['opening_time'] = datetime.strptime(shop_data['opening_time'], '%H:%M:%S').time()
                    shop_data['closing_time'] = datetime.strptime(shop_data['closing_time'], '%H:%M:%S').time()

                    # ✅ Step 3: Decode image files
                    shop_logo_data = request.session.get('shop_logo')
                    shop_logo_name = request.session.get('shop_logo_file', 'logo.png')
                    shop_logo_file = ContentFile(base64.b64decode(shop_logo_data), name=shop_logo_name) if shop_logo_data else None

                    ownership_data = request.session.get('ownership_proof')
                    ownership_name = request.session.get('ownership_file', 'proof.png')
                    ownership_file = ContentFile(base64.b64decode(ownership_data), name=ownership_name) if ownership_data else None

                    # ✅ Step 4: Create Shop object
                    shop = Shop.objects.create(
                        owner=user,
                        shop_name=shop_data['shop_name'],
                        shop_category=shop_data['shop_category'],
                        shop_address=shop_data['shop_address'],
                        city=shop_data['city'],
                        gst_number=shop_data['gst_number'],
                        shop_logo=shop_logo_file,
                        ownership_proof=ownership_file,
                        opening_time=shop_data['opening_time'],
                        closing_time=shop_data['closing_time'],
                    )

                    # ✅ Step 5: Link selected delivery pincodes from session
                    pin_ids = request.session.get('delivery_pincodes', [])
                    if pin_ids:
                        print("📦 Delivery pin IDs:", pin_ids)

                    shop.delivery_pincodes.set(PinCode.objects.filter(id__in=pin_ids))  # ✅ This line links pin codes                       

                    # ✅ Step 6: Save bank info
                    ShopBankInfo.objects.create(shop=shop, **form.cleaned_data)

                    # ✅ Step 7: Clear session data
                    keys_to_clear = [
                        'owner_user_data', 'owner_shop_data', 'delivery_pincodes',
                        'shop_logo', 'ownership_proof', 'shop_logo_file', 'ownership_file'
                    ]
                    for key in keys_to_clear:
                        request.session.pop(key, None)

                    # ✅ Step 8: Login and redirect
                    messages.success(request, "Registration successful!")
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    return redirect('shop_owner_dashboard')

            except Exception as e:
                messages.error(request, f"Registration failed: {e}")

    else:
        form = ShopBankForm()

    return render(request, 'shop/register_owner_step3.html', {'form': form})


from django.shortcuts import render, redirect
from django.contrib import messages

def verify_owner_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        actual_otp = request.session.get('otp')

        if entered_otp == actual_otp:
            # OTP matched — proceed to next step
            return redirect('register_owner_step2')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'shop/verify_otp.html')  # your OTP input template

@login_required
def edit_shop_profile(request):
    shop = Shop.objects.get(owner=request.user)

    if request.method == 'POST':
        form = EditShopProfileForm(request.POST, instance=shop)

        if form.is_valid():
            form.save()

            # handle pin codes
            pincode_ids = request.POST.getlist('pincodes')
            shop.delivery_pincodes.set(pincode_ids)  # many-to-many relation

            return redirect('shop_owner_dashboard')
  # or wherever you want
    else:
        form = EditShopProfileForm(instance=shop)

    all_pincodes = PinCode.objects.all()
    current_pincodes = shop.delivery_pincodes.all()


    return render(request, 'shop/edit_shop_profile.html', {
        'form': form,
        'all_pincodes': all_pincodes,
        'current_pincodes': current_pincodes
    })

@login_required
def owner_profiles(request):
    print("Logged in user:", request.user)
    
    shop = Shop.objects.filter(owner=request.user).first()
    print("Shop found:", shop)

    bank = None
    if shop:
        bank = ShopBankInfo.objects.filter(shop=shop).first()
        print("Bank info found:", bank)

    return render(request, 'shop/owner_profiles.html', {
        'user': request.user,
        'shop': shop,
        'bank': bank,
    })

# @login_required
# def edit_bank_details(request):
#     shop = Shop.objects.filter(owner=request.user).first()
#     if not shop:
#         messages.error(request, "Shop not found.")
#         return redirect('owner_profiles')

#     bank = ShopBankInfo.objects.filter(shop=shop).first()

#     if not bank:
#         messages.error(request, "Bank details not found.")
#         return redirect('owner_profiles')
    
from django.contrib import messages
from shop.form_parts.bank_edit_form import EditBankDetailsForm
from shop.models import Shop, ShopBankInfo

@login_required
def edit_bank_details(request):
    shop = Shop.objects.filter(owner=request.user).first()
    if not shop:
        messages.error(request, "Shop not found.")
        return redirect('owner_profiles')

    bank = ShopBankInfo.objects.filter(shop=shop).first()
    if not bank:
        messages.error(request, "Bank details not found.")
        return redirect('owner_profiles')

    if request.method == 'POST':
        form = EditBankDetailsForm(request.POST, instance=bank)
        if form.is_valid():
            form.save()
            messages.success(request, "Bank details updated successfully.")
            return redirect('owner_profiles')
    else:
        form = EditBankDetailsForm(instance=bank)

    return render(request, 'shop/edit_bank_details.html', {'form': form})
from django.db.models import Sum

@login_required
def shop_product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, shop__owner=request.user)
    total_orders = OrderItem.objects.filter(product=product).count()
    total_revenue = OrderItem.objects.filter(product=product).aggregate(total=Sum('price'))['total'] or 0
    return render(request, 'shop/shop_product_detail.html', {
        'product': product,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
    })

def select_role_view(request):
    return render(request, 'shop/select_role.html')

def create_shop(request):
    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES)
        if form.is_valid():
            shop = form.save(commit=False)
            shop.owner = request.user  # ya jo bhi logic ho
            shop.save()
            form.save_m2m()  # ✅ THIS LINE IS MUST for ManyToMany like delivery_pincodes
            messages.success(request, "Shop created!")
            return redirect('shop_dashboard')

@login_required
def edit_shop(request):
    shop = get_object_or_404(Shop, owner=request.user)

    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES, instance=shop)
        if form.is_valid():
            form.save()
            messages.success(request, "Shop updated successfully.")
            return redirect('shop_owner_dashboard')
    else:
        form = ShopForm(instance=shop)

    return render(request, 'shop/edit_shop.html', {'form': form})

def update_cart(request):
    if request.method == "POST":
        for key, value in request.POST.items():
            if key.startswith("quantity_"):
                try:
                    cart_item_id = int(key.split("_")[1])
                    quantity = int(value)
                    item = CartItem.objects.get(id=cart_item_id, user=request.user)
                    item.quantity = quantity
                    item.save()
                except (ValueError, CartItem.DoesNotExist):
                    continue
        return redirect('cart_view')  # Use your actual cart page view name here
    return redirect('cart_view')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import CartItem
@csrf_exempt
def update_cart_quantity_ajax(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity'))

        cart_item = CartItem.objects.get(id=item_id, user=request.user)
        cart_item.quantity = quantity
        cart_item.save()

        return JsonResponse({'status': 'success'})

def shipping_address_update(request):
    if request.method == 'POST':
        address_line1 = request.POST.get('address_line1', '')
        address_line2 = request.POST.get('address_line2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        country = request.POST.get('country', '')
        pin_code = request.POST.get('pin_code', '')

        request.session['shipping_address'] = {
            'address_line1': address_line1,
            'address_line2': address_line2,
            'city': city,
            'state': state,
            'country': country,
            'pin_code': pin_code,
        }
        from django.contrib import messages
        messages.success(request, "Shipping address updated!")
        return redirect('cart_view')

    shipping_address = request.session.get('shipping_address', {
        'address_line1': getattr(request.user, 'address_line1', ''),
        'address_line2': getattr(request.user, 'address_line2', ''),
        'city': getattr(request.user, 'city', ''),
        'state': getattr(request.user, 'state', ''),
        'country': getattr(request.user, 'country', ''),
        'pin_code': getattr(request.user, 'pin_code', ''),
    })
    return render(request, 'shop/shipping_address_update.html', {'shipping_address': shipping_address})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    items = order.items.select_related('product')
    return render(request, 'shop/order_detail.html', {
        'order': order,
        'items': items,
    })

@login_required
def rider_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, delivery_rider=request.user)
    items = order.items.select_related('product')
    if request.method == 'POST' and request.POST.get('action') == 'mark_delivered':
        if order.rider_status == 'accepted' and order.status == 'out_for_delivery':
            order.status = 'delivered'
            order.save()
            messages.success(request, f'Order #{order.id} marked as Delivered!')
            return redirect('rider_order_detail', order_id=order.id)
    return render(request, 'shop/order_detail.html', {
        'order': order,
        'items': items,
    })

@login_required
def rider_dashboard(request):
    # raise Exception('TEST RIDER DASHBOARD')  # Removed test exception
    if request.user.role != 'rider':
        return redirect('home')

    # Handle POST for toggling duty status
    if request.method == 'POST' and 'toggle_duty' in request.POST:
        request.user.on_duty = not request.user.on_duty
        request.user.save()
        messages.info(request, f'You are now {"On Duty" if request.user.on_duty else "Off Duty"}.')
        return redirect('rider_dashboard')

    # Show all orders assigned to the rider
    orders = Order.objects.filter(
        delivery_rider=request.user
    ).prefetch_related('items__product', 'customer')

    # Stats for Earnings & Stats
    all_assigned_orders = Order.objects.filter(delivery_rider=request.user)
    total_assigned = all_assigned_orders.count()
    total_rejected = all_assigned_orders.filter(rider_status='declined').count()
    total_selected = all_assigned_orders.filter(rider_status='accepted').count()
    total_delivered = all_assigned_orders.filter(status='delivered').count()
    total_pending = all_assigned_orders.filter(rider_status='accepted', status='out_for_delivery').count()

    print('DEBUG Rider Dashboard Stats:')
    print('total_assigned:', total_assigned)
    print('total_rejected:', total_rejected)
    print('total_selected:', total_selected)
    print('total_delivered:', total_delivered)
    print('total_pending:', total_pending)

    # Handle POST for status update or rejection
    if request.method == 'POST' and 'order_id' in request.POST:
        order_id = request.POST.get('order_id')
        action = request.POST.get('action')
        order = Order.objects.get(id=order_id, delivery_rider=request.user)
        if action == 'reject':
            order.rider_status = 'declined'
            # Assign next backup rider if available
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
                order.status = 'confirmed'  # Or another status to indicate needs reassignment
                order.save()
                messages.warning(request, f'All backup riders rejected Order #{order.id}. Please reassign.')
            return redirect('rider_dashboard')
        elif action == 'accept' and order.rider_status == 'pending' and order.status == 'shipped':
            order.rider_status = 'accepted'
            order.status = 'out_for_delivery'
            order.save()
            messages.success(request, f'Order #{order.id} accepted and marked as Out for Delivery.')
            return redirect('rider_dashboard')
        elif action == 'mark_delivered' and order.rider_status == 'accepted' and order.status == 'out_for_delivery':
            order.status = 'delivered'
            order.save()
            messages.success(request, f'Order #{order.id} marked as Delivered!')
            return redirect('rider_dashboard')
    return render(request, 'users/rider_dashboard.html', {
        'assigned_deliveries': orders,
        'rider': request.user,
        'on_duty': request.user.on_duty,
        'total_assigned': total_assigned,
        'total_rejected': total_rejected,
        'total_selected': total_selected,
        'total_delivered': total_delivered,
        'total_pending': total_pending,
    })