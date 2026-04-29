from django import forms
from users.models import CustomUser
from shop.models import Shop, PinCode
from shop.fields import DeliveryPinCodeField

class OwnerPersonalEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

class OwnerShopForm(forms.ModelForm):
    delivery_pincodes = DeliveryPinCodeField(
        queryset=PinCode.objects.all(),
        required=False,
        label="Delivery Pin Codes"
    )

    class Meta:
        model = Shop
        fields = [
            'shop_name', 'shop_category', 'shop_address', 'city', 
            'gst_number', 'opening_time', 'closing_time', 
            'shop_logo', 'ownership_proof', 'delivery_pincodes'
        ]
        widgets = {
            'shop_name': forms.TextInput(attrs={'class': 'form-control'}),
            'shop_category': forms.TextInput(attrs={'class': 'form-control'}),
            'shop_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'gst_number': forms.TextInput(attrs={'class': 'form-control'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'shop_logo': forms.FileInput(attrs={'class': 'form-control'}),
            'ownership_proof': forms.FileInput(attrs={'class': 'form-control'}),
        }

class DeliveryPinCodeForm(forms.ModelForm):
    delivery_pincodes = DeliveryPinCodeField(
        queryset=PinCode.objects.all(),
        required=False
    )

    class Meta:
        model = Shop
        fields = ['delivery_pincodes']
