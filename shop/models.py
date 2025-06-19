from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

# Custom user model
# class CustomUser(AbstractUser):
#     phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
#     address = models.TextField(null=True, blank=True)
#     pin_code = models.CharField(max_length=10, null=True, blank=True)

#     ROLE_CHOICES = (
#         ('customer', 'Customer'),
#         ('shop_owner', 'Shop Owner'),
#     )
#     role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

#     USERNAME_FIELD = 'username'

#     def __str__(self):
#         return self.username

# Product model (updated)
class Product(models.Model):
    shop_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'shop_owner'})
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    def __str__(self):
        return self.name


# CartItem model
class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

from django.db import models
from django.conf import settings

class Order(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order #{self.id} by {self.customer.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
