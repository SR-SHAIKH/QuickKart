from django.db import models
from django.conf import settings
from users.models import CustomUser


class PinCode(models.Model):
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.code
# ✅ Product Model
class Product(models.Model):
    shop_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'shop_owner'}
    )
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)

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
        ('delivered', 'Delivered'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

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
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    shop_name = models.CharField(max_length=100)  # changed from `name`
    shop_logo = models.ImageField(upload_to='shop_logos/', blank=True, null=True)  # changed from `logo`
    shop_category = models.CharField(max_length=100)
    shop_address = models.TextField()
    city = models.CharField(max_length=100)  # ✅ already present in your version
    gst_number = models.CharField(max_length=20)
    ownership_proof = models.FileField(upload_to='ownership_proofs/', blank=True, null=True)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    
    delivery_pincodes = models.ManyToManyField('PinCode', blank=True)

    def __str__(self):
        return self.shop_name

# Add this at the end of shop/models.py
class ShopBankInfo(models.Model):
    shop = models.OneToOneField('Shop', on_delete=models.CASCADE)
    account_holder_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    ifsc_code = models.CharField(max_length=11)
    bank_name = models.CharField(max_length=100)
    
    # 🔻 Add these fields:
    preferred_payment_method = models.CharField(
        max_length=50,
        choices=[('bank', 'Bank Transfer'), ('upi', 'UPI')],
        default='bank'
    )
    upi_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.shop.shop_name} - {self.bank_name}"

class Brand(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='brand_logos/', blank=True, null=True)

    def __str__(self):
        return self.name