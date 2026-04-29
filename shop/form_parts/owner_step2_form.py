from django import forms
from shop.models import Shop, PinCode
from shop.fields import DeliveryPinCodeField

class RegisterShopForm(forms.ModelForm):
    delivery_pincodes = DeliveryPinCodeField(
        queryset=PinCode.objects.all(),
        required=False,
        label="Delivery Pin Codes"
    )

    class Meta:
        model = Shop
        fields = [
            'shop_name',
            'shop_category',
            'shop_address',
            'city',
            'shop_logo',
            'ownership_proof',
            'gst_number',
            'opening_time',
            'closing_time',
            'delivery_pincodes',
        ]
        widgets = {
            'opening_time': forms.TimeInput(attrs={'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time'}),
        }
