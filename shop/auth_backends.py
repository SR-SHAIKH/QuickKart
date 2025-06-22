from django.contrib.auth.backends import ModelBackend
from users.models import CustomUser

class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        user = None
        try:
            if '@' in username:
                user = CustomUser.objects.filter(email=username).first()
            else:
                user = CustomUser.objects.filter(phone=username).first()
        except Exception as e:
            return None

        if user and user.check_password(password):
            return user
        return None


