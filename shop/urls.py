# from .views import home
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from users import views as user_views
from django.contrib.auth import views as auth_views
from users.views import CustomPasswordChangeView
from .views import edit_customer_profile

urlpatterns = [
    # 🌐 Public
    path('', views.home, name='home'),
    path('cart/', views.cart_view, name='cart_view'),

    # 🔐 Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),

    # users/urls.py
    

    path('verify-otp/', views.verify_otp, name='verify_otp'),

    # 👤 Customer
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    # path('products/', views.product_list, name='product_list'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', views.wishlist_page, name='wishlist'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.my_orders, name='my_orders'),
    path('order-success/', views.order_success, name='order_success'),

    # 👤 Customer Profile
    path('dashboard/customer/profile/', user_views.customer_profile_view, name='customer_profile'),
    path('dashboard/customer/edit-profile/', user_views.customer_edit_profile, name='customer_edit_profile'),

    # 🛍️ Shop Owner Profile
    path('dashboard/shop/profile/', user_views.owner_profile_view, name='owner_profile'),
    path('dashboard/shop/edit-profile/', user_views.owner_edit_profile, name='owner_edit_profile'),

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
    path('buy/<int:product_id>/', views.buy_now, name='buy_now'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('ajax/toggle_wishlist/', views.toggle_wishlist_ajax, name='toggle_wishlist'),
    path('toggle-wishlist/', views.toggle_wishlist_ajax, name='toggle_wishlist'), # doubble duplicated
    path('wishlist/', views.wishlist_page, name='view_wishlist'),
    path('profile/customer/edit/', edit_customer_profile, name='edit_profile'),
    path('logout/', views.logout_view, name='logout'),
    path('wishlist/', views.wishlist_page, name='wishlist_page'),
    path('search/', views.search_view, name='search'),
    path('orders/history/', views.order_history, name='order_history'),
    path('category/<int:category_id>/', views.products_by_category, name='products_by_category'),
    path('register/owner/step1/', views.register_owner_step1, name='register_owner_step1'),
    path('register/owner/step2/', views.register_owner_step2, name='register_owner_step2'),
    path('register/owner/step3/', views.register_owner_step3, name='register_owner_step3'),
    path('register/select/', views.select_role_view, name='select_role'),
    path('register/owner/verify-otp/', views.verify_owner_otp, name='verify_owner_otp'),
    path('shop/edit/', views.edit_shop_profile, name='edit_shop_profile'),
    path('owner/profiles/', views.owner_profiles, name='owner_profiles'),
    path('owner/edit-bank/', views.edit_bank_details, name='edit_bank_details'),
    # path('edit-bank/', views.edit_bank_details, name='edit_bank_details'),
    path('dashboard/shop/product/<int:product_id>/', views.shop_product_detail, name='shop_product_detail'),
    path('owner/product/<int:pk>/', views.owner_product_detail, name='owner_product_detail'),
    path('owner/dashboard/', views.shop_owner_dashboard, name='dashboard_owner'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),

]

# 📦 Media
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

