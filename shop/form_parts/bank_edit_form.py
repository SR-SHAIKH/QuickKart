from django import forms
from shop.models import ShopBankInfo

class EditBankDetailsForm(forms.ModelForm):
    class Meta:
        model = ShopBankInfo
        fields = ['account_holder_name', 'bank_name', 'account_number', 'ifsc_code', 'upi_id']
        widgets = {
            'account_number': forms.TextInput(attrs={'type': 'number'}),
        }
class EditBankDetailsForm(forms.ModelForm):
    class Meta:
        model = ShopBankInfo
        fields = ['account_holder_name', 'bank_name', 'account_number', 'ifsc_code', 'upi_id']

    def clean_account_number(self):
        account_number = self.cleaned_data.get('account_number')
        if not account_number.isdigit():
            raise forms.ValidationError("Account number must contain only digits.")
        return account_number