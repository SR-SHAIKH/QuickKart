from django.urls import path
from django.contrib.auth import views as auth_views
from .views import CustomPasswordChangeView, profile_view, edit_profile

urlpatterns = [
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('password/change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password/change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='users/password_change_done.html'
    ), name='password_change_done'),
]
