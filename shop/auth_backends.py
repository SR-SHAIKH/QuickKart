from django.contrib.auth.backends import ModelBackend
from shop.models import CustomUser

class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(email=username)
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(phone=username)
            except CustomUser.DoesNotExist:
                return None

        if user.check_password(password):
            return user
        return None
