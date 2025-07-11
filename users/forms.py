from django import forms
from .models import CustomUser
from shop.models import PinCode
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'confirm_password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise ValidationError("Passwords do not match.")
        return cleaned_data

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'alt_phone', 'address_line1', 'address_line2',
            'city', 'state', 'pin_code', 'profile_picture'
        ]

        widgets = {
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-input'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-input'}),
            'city': forms.TextInput(attrs={'class': 'form-input'}),
            'state': forms.TextInput(attrs={'class': 'form-input'}),
            'pin_code': forms.TextInput(attrs={'class': 'form-input'}),
        }

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
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control rounded-3 shadow-sm'
            })

        # 🧽 Remove unwanted text from profile_picture field
        self.fields['profile_picture'].widget.clear_checkbox_label = ''
        self.fields['profile_picture'].widget.initial_text = ''
        self.fields['profile_picture'].widget.input_text = ''

class RiderRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    delivery_pincodes = forms.ModelMultipleChoiceField(
        queryset=PinCode.objects.none(),  # Set in __init__
        widget=forms.CheckboxSelectMultiple,
        required=False,  # Not required, since handled via JS
        label='Delivery Areas (Pin Codes)'
    )
    address = forms.CharField(label='Address', widget=forms.Textarea(attrs={'rows': 2}), required=False)
    profile_picture = forms.ImageField(label='Profile Picture', required=False)
    gender = forms.ChoiceField(choices=(('male', 'Male'), ('female', 'Female'), ('other', 'Other')), required=False)
    date_of_birth = forms.DateField(label='Date of Birth', widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    alt_phone = forms.CharField(label='Alternate Phone', required=False)
    vehicle_type = forms.ChoiceField(
        label='Vehicle Type',
        choices=[
            ('', 'Select Vehicle Type'),
            ('bicycle', 'Bicycle'),
            ('bike', 'Bike'),
            ('electric_bike', 'Electric Bike'),
            ('scooter', 'Scooter/Scooty'),
            ('car', 'Car'),
            ('other', 'Other'),
        ],
        required=False
    )
    vehicle_number = forms.CharField(label='Vehicle Number', required=False)
    id_proof = forms.FileField(label='ID Proof', required=False)

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'alt_phone',
            'password1', 'password2',
            'delivery_pincodes', 'address', 'profile_picture',
            'gender', 'date_of_birth', 'vehicle_type', 'vehicle_number', 'id_proof'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['delivery_pincodes'].queryset = PinCode.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'rider'
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            self.save_m2m()
        return user
