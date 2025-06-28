from django.urls import path
from . import views

urlpatterns = [
    # ✅ Customer
    path('profile/customer/', views.customer_profile_view, name='customer_profile'),
    path('profile/customer/edit/', views.customer_edit_profile, name='customer_edit_profile'),

    # ✅ Shop Owner
    path('profile/owner/', views.owner_profile_view, name='owner_profile'),
    path('profile/owner/edit/', views.owner_edit_profile, name='owner_edit_profile'),

    # ✅ Password Change
    path('password/change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('register/', views.register, name='register'),
    path('register/customer/', views.customer_register_otp, name='customer_register_otp'),
    path('register/customer/verify-otp/', views.verify_customer_otp, name='verify_customer_otp'),
]
