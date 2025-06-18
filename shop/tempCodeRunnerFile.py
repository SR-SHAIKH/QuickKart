import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

from .models import Product, CartItem, CustomUser
from .forms import RegistrationForm


# ------------------ Home Page ------------------
def home(request):
    products = Product.objects.all()
    return render(request, 'shop/home.html', {'products': products})


# ------------------ Login Page ------------------
def login_view(request):
    return render(request, 'shop/login.html')  # Make sure template exists


# ------------------ OTP Utility ------------------
def generate_otp():
    return random.randint(100000, 999999)

def send_otp_email(email, otp):
    send_mail(
        'Your OTP Verification Code',
        f'Your OTP code is {otp}',
        'your_email@example.com',  # This will be overridden by settings.EMAIL_HOST_USER
        [email],
        fail_silently=False,
    )


# ------------------ Registration View ------------------
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            request.session['registration_data'] = form.cleaned_data
            otp = generate_otp()
            request.session['otp'] = str(otp)

            send_otp_email(form.cleaned_data['email'], otp)
            return redirect('verify_otp')
        else:
            # Invalid form - re-render with errors
            return render(request, 'shop/register.html', {'form': form})
    else:
        form = RegistrationForm()
    return render(request, 'shop/register.html', {'form': form})



# ------------------ OTP Verification ------------------
def verify_otp(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')

        if user_otp == session_otp:
            data = request.session.get('registration_data')
            user = CustomUser.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password1'],
                phone=data['phone'],
                address=data['address'],
                pin_code=data['pin_code'],
            )
            # Clear session
            request.session.pop('otp')
            request.session.pop('registration_data')

            return redirect('login')
        else:
            return render(request, 'shop/verify_otp.html', {'error': 'Invalid OTP'})
    
    return render(request, 'shop/verify_otp.html')


# ------------------ Cart Views ------------------
@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total': total})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')


@login_required
def remove_from_cart(request, item_id):
    CartItem.objects.filter(id=item_id, user=request.user).delete()
    return redirect('cart')
