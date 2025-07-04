# owner_step3_form.py
from django import forms
from shop.models import ShopBankInfo

class ShopBankForm(forms.ModelForm):
    class Meta:
        model = ShopBankInfo
        fields = [
            'payment_method',
            'account_holder_name',
            'account_number',
            'ifsc_code',
            'bank_name',
            'upi_id',
        ]
        widgets = {
            'payment_method': forms.Select(
                choices=ShopBankInfo.PAYMENT_CHOICES,  # ✅ Use model constant directly
                attrs={'class': 'form-select'}
            ),
            'account_holder_name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'ifsc_code': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'upi_id': forms.TextInput(attrs={'class': 'form-control'}),
        }
