from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    # ✅ Customer
    path('profile/customer/', views.customer_profile_view, name='customer_profile'),
    path('profile/customer/edit/', views.customer_edit_profile, name='customer_edit_profile'),

    # ✅ Password Change
    path('password/change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('register/', views.register, name='register'),
    path('register/customer/', views.customer_register_otp, name='customer_register_otp'),
    path('register/customer/verify-otp/', views.verify_customer_otp, name='verify_customer_otp'),
    path('register/rider/', views.rider_register, name='rider_register'),
    path('dashboard/rider/', views.rider_dashboard, name='rider_dashboard'),  # Removed to avoid conflict
    path('dashboard/rider/edit-profile/', views.rider_edit_profile, name='rider_edit_profile'),
]
