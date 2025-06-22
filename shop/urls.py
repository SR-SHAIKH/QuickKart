from django.urls import path
from . import views

urlpatterns = [
    # 🌐 Public/Home
    path('', views.home, name='home'),

    # 🔐 Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),

    # 👤 Dashboards
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/shop/', views.shop_owner_dashboard, name='shop_owner_dashboard'),
    path('dashboard/shop/products/', views.shop_owner_products, name='shop_owner_products'),
    path('dashboard/shop/orders/', views.shop_owner_orders, name='shop_owner_orders'),

    # 🛒 Cart (Customer Only)
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # 🛍️ Product CRUD (Shop Owner Only)
    path('products/create/', views.create_product, name='create_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),

    # 📋 Product List for Customers
    path('products/', views.product_list, name='product_list'),

    # 💳 Checkout
    path('checkout/', views.checkout, name='checkout'),
]
