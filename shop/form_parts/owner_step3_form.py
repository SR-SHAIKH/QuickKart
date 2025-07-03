from django import forms
from shop.models import ShopBankInfo

class ShopBankForm(forms.ModelForm):
    class Meta:
        model = ShopBankInfo
        fields = [
            'payment_method',          # This is correct as per your model
            'account_holder_name',
            'account_number',
            'ifsc_code',
            'bank_name',
            'upi_id',
        ]
        widgets = {
            'payment_method': forms.Select(choices=[
                ('bank', 'Bank Transfer'),
                ('upi', 'UPI'),
                ('both', 'Both'),
            ])
        }
