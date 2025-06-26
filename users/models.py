from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string

ROLE_CHOICES = (
    ('customer', 'Customer'),
    ('shop_owner', 'Shop Owner'),
)

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
)

class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)

    # Contact Info
    phone = models.CharField(max_length=15, blank=True, default='')
    alt_phone = models.CharField(max_length=15, blank=True, null=True)

    # Personal Info
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    # Address Info
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    pin_code = models.CharField(max_length=10, blank=True)

    # Profile Pic
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    # Role (customer / shop_owner)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        # Auto-generate a unique username if not provided
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
