from django import forms
from shop.models import ShopBankInfo

class ShopBankForm(forms.ModelForm):
    class Meta:
        model = ShopBankInfo
        fields = [
            'account_holder_name',
            'bank_name',
            'account_number',
            'ifsc_code',
            'upi_id',
            'preferred_payment_method',
        ]
        widgets = {
            'preferred_payment_method': forms.Select(choices=[
                ('Bank', 'Bank'),
                ('UPI', 'UPI'),
            ])
        }
