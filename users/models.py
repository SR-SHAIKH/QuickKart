from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.crypto import get_random_string
ROLE_CHOICES = (
    ('customer', 'Customer'),
    ('shop_owner', 'Shop Owner'),
    ('rider', 'Delivery Rider'),
)

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
)

# ✅ Custom User Manager
class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if not user.username:
            # Auto-generate username if not present
            base_username = "user_"
            while True:
                new_username = base_username + get_random_string(8)
                if not self.model.objects.filter(username=new_username).exists():
                    user.username = new_username
                    break
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)

# ✅ Custom User Model
class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)

    phone = models.CharField(max_length=15, blank=True, default='')
    alt_phone = models.CharField(max_length=15, blank=True, null=True)

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    pin_code = models.CharField(max_length=10, blank=True)

    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    delivery_pincodes = models.ManyToManyField('shop.PinCode', blank=True)
    on_duty = models.BooleanField(default=False, help_text='Is the rider currently available for delivery?')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # ✅ Attach custom manager
    objects = CustomUserManager()

    def __str__(self):
        return self.email


class CustomerProfile(models.Model):
    from django.conf import settings
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender_choices = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(max_length=1, choices=gender_choices, blank=True)
    country = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.user.email