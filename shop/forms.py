from django import forms
from users.models import CustomUser
from .models import Product

# ---------------------- #
# 1. Registration Form
# ---------------------- #
class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = [
            'email', 'phone', 'address_line1', 'address_line2',
            'city', 'state', 'country', 'pin_code', 'role'
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and (not phone.isdigit() or len(phone) != 10):
            raise forms.ValidationError("Enter a valid 10-digit phone number.")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


# ---------------------- #
# 2. Product Form
# ---------------------- #
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'image', 'description', 'stock', 'category']


# -------------------------------- #
# 3. Profile Edit Form for Customer
# -------------------------------- #
class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email',
            'phone', 'alt_phone',
            'gender', 'date_of_birth',
            'address_line1', 'address_line2', 
            'city', 'state', 'country', 'pin_code',
            'profile_picture',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }



# ---------------------------- #
# 4. Profile Edit Form for Owner
# ---------------------------- #
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'alt_phone',
            'gender', 'date_of_birth',
            'address_line1', 'address_line2', 'city', 'state', 'country',
            'pin_code', 'profile_picture'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'profile_picture': forms.FileInput(),
        }
