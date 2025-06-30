from django import forms
from users.models import CustomUser
from .models import Product
from shop.form_parts import ShopForm
from django.shortcuts import render, redirect
from .models import Shop

ROLE_CHOICES = [
    ('customer', 'Customer'),
    ('shop_owner', 'Shop Owner'),
]

# ✅ Customer registration form

class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=ROLE_CHOICES)

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
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.role = self.cleaned_data["role"]
        if commit:
            user.save()
        return user


# ✅ Shop owner step 1 (for OTP + basic details)
class ShopOwnerStep1Form(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['email', 'phone']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class OwnerPersonalForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
            return cleaned_data  # ✅ Add this line




def register_owner_step2(request):
    if 'owner_user_data' not in request.session:
        return redirect('register_owner_step1')

    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES)
        if form.is_valid():
            shop_data = form.cleaned_data
            request.session['owner_shop_data'] = {
                field: form.cleaned_data[field]
                for field in form.fields if field != 'delivery_pincodes'  # ✅ correct field name
            }
            request.session['delivery_pincodes'] = list(
                form.cleaned_data['delivery_pincodes'].values_list('id', flat=True)
            )
            return redirect('register_owner_step3')
    else:
        form = ShopForm()
    return render(request, 'shop/register_owner_step2.html', {'form': form})


from .models import ShopBankInfo

class ShopBankForm(forms.ModelForm):
    class Meta:
        model = ShopBankInfo
        exclude = ['shop']  # Shop will be assigned in the view

from .models import PinCode

class EditShopProfileForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = [
            'shop_name',
            'shop_category',
            'shop_address',
            'shop_logo',
            'ownership_proof',
            'gst_number',
            'opening_time',
            'closing_time',
            'delivery_pincodes',
            'city',
        ]
        widgets = {
            'delivery_pincodes': forms.CheckboxSelectMultiple,
            'opening_time': forms.TimeInput(attrs={'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super(EditShopProfileForm, self).__init__(*args, **kwargs)
        self.fields['shop_name'].label = "Shop Name"

