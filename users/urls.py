from django.urls import path
from . import views

urlpatterns = [
    path('profile/customer/', views.customer_profile_view, name='customer_profile'),
    path('profile/customer/edit/', views.customer_edit_profile, name='customer_edit_profile'),

    path('profile/owner/', views.owner_profile_view, name='owner_profile'),
    path('profile/owner/edit/', views.owner_edit_profile, name='owner_edit_profile'),

    path('profile/edit/', views.edit_profile, name='profile'),  # Optional if you use one route for both

    path('password/change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
]
