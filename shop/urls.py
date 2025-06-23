from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from users import views as user_views
from django.contrib.auth import views as auth_views
from users.views import CustomPasswordChangeView

urlpatterns = [
    # 🌐 Public
    path('', views.home, name='home'),

    # 🔐 Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),

    # 👤 Customer
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.my_orders, name='my_orders'),
    path('order-success/', views.order_success, name='order_success'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    # 👤 Profile (shared for both roles)
    path('dashboard/profile/', user_views.profile_view, name='profile'),
    path('dashboard/edit-profile/', user_views.edit_profile, name='edit_profile'),

    # 🔐 Optional password change
    path('dashboard/change-password/', user_views.CustomPasswordChangeView.as_view(), name='password_change'),

    # 🛍️ Shop Owner
    path('dashboard/shop/', views.shop_owner_dashboard, name='shop_owner_dashboard'),
    path('dashboard/shop/products/', views.shop_owner_products, name='shop_owner_products'),
    path('dashboard/shop/orders/', views.shop_owner_orders, name='shop_owner_orders'),
    path('products/create/', views.create_product, name='create_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),

    # 🚴 Rider (planned, can be uncommented when ready)
    # path('dashboard/rider/', views.rider_dashboard, name='rider_dashboard'),
    
    path('dashboard/change-password-done/', auth_views.PasswordChangeDoneView.as_view(
       template_name='users/password_change_done.html'
    ), name='password_change_done'),
    path('dashboard/change-password/', CustomPasswordChangeView.as_view(), name='password_change'),

]

# 📦 Media
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
