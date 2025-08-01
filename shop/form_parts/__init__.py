from .owner_step1_form import OwnerPersonalForm
from .owner_step2_form import ShopForm
from .owner_step3_form import ShopBankForm

from .registration_form import RegistrationForm
from .product_form import ProductForm
from .customer_profile_form import CustomerProfileForm

def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['phone'].required = True
    self.fields['gender'].required = True
    self.fields['date_of_birth'].required = True
