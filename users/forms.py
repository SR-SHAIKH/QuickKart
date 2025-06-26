from django import forms
from .models import CustomUser


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
