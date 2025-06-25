from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string

ROLE_CHOICES = (
    ('customer', 'Customer'),
    ('shop_owner', 'Shop Owner'),
)

class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)

    phone = models.CharField(max_length=15, default='Not Provided')
    address = models.TextField(default='Not Provided')
    pin_code = models.CharField(max_length=10, default='000000')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if not self.username:
            base_username = "user_"
            while True:
                new_username = base_username + get_random_string(8)
                if not CustomUser.objects.filter(username=new_username).exists():
                    self.username = new_username
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
