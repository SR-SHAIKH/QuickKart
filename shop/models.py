from django.db import models
from django.conf import settings
from users.models import CustomUser


class PinCode(models.Model):
    code = models.CharField(max_length=10, unique=True)
    area_name = models.CharField(max_length=100)

    def __str__(self):
        return self.code
# ✅ Product Model
from django.conf import settings
from django.db import models

class Product(models.Model):
    shop_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'shop_owner'}
    )
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE, related_name='products')  # ✅ Add this line

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)

    is_active = models.BooleanField(default=True) 

    def __str__(self):
        return self.name

# ✅ CartItem Model
class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

# ✅ Order Model
class Order(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    delivery_address = models.TextField()
    phone = models.CharField(max_length=15)
    order_date = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    RIDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    rider_status = models.CharField(max_length=10, choices=RIDER_STATUS_CHOICES, default='pending')

    delivery_rider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        limit_choices_to={'role': 'rider'},
        on_delete=models.SET_NULL,
        related_name='assigned_orders',
    )

    backup_riders = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='backup_orders',
        blank=True,
        limit_choices_to={'role': 'rider'}
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.id} by {self.customer.username}"

# ✅ OrderItem Model (uses Option 1: 'shop.Order')
class OrderItem(models.Model):
    order = models.ForeignKey('shop.Order', related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # price at time of order

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.email} - {self.product.name}"
    
# In shop/models.py

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Shop(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shop')
    name = models.CharField(max_length=255)  # 👈 Ye line honi chahiye
    address = models.TextField() 

    shop_name = models.CharField(max_length=100)
    shop_logo = models.ImageField(upload_to='shop_logos/', blank=True, null=True)
    shop_category = models.CharField(max_length=100)
    shop_address = models.TextField()
    city = models.CharField(max_length=100)
    gst_number = models.CharField(max_length=20)
    ownership_proof = models.FileField(upload_to='ownership_proofs/', blank=True, null=True)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    
    delivery_pincodes = models.ManyToManyField('PinCode', blank=True, related_name='shops')


    def __str__(self):
        return self.shop_name


# Add this at the end of shop/models.py
class ShopBankInfo(models.Model):
    PAYMENT_CHOICES = [
        ('bank', 'Bank Transfer'),
        ('upi', 'UPI'),
        ('both', 'Both'),
    ]

    shop = models.OneToOneField('Shop', on_delete=models.CASCADE)
    
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='bank')  # ✅ NEW FIELD

    account_holder_name = models.CharField(max_length=255, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    logo = models.ImageField(upload_to='shop_logos/', null=True, blank=True)

    upi_id = models.CharField(max_length=100, blank=True, null=True)
    PREFERRED_CHOICES = [
        ('bank', 'Bank Transfer'),
        ('upi', 'UPI'),
        ('both', 'Both'),
    ]

    def __str__(self):
        return f"{self.shop.shop_name} - Bank Info"

class Brand(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='brand_logos/', blank=True, null=True)

    def __str__(self):
        return self.name