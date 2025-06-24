# users/urls.py

from django.urls import path
from .views import (
    CustomPasswordChangeView,
    customer_profile_view,
    customer_edit_profile,
    owner_profile_view,
    owner_edit_profile,
)

urlpatterns = [
    # 👤 Customer URLs
    path('customer/profile/', customer_profile_view, name='customer_profile'),
    path('customer/edit-profile/', customer_edit_profile, name='customer_edit_profile'),

    # 🛍️ Shop Owner URLs
    path('owner/profile/', owner_profile_view, name='owner_profile'),
    path('owner/edit-profile/', owner_edit_profile, name='owner_edit_profile'),

    # 🔐 Password Change
    path('change-password/', CustomPasswordChangeView.as_view(), name='password_change'),
]
