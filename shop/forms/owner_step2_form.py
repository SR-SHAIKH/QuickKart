from django import forms
from shop.models import Shop

class ShopForm(forms.ModelForm):
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
        ]
        widgets = {
            'delivery_pincodes': forms.CheckboxSelectMultiple,
            'opening_time': forms.TimeInput(attrs={'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time'}),
        }
