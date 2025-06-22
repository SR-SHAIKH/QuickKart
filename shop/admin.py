from django.contrib import admin
from django import forms
from shop.models import Product
from users.models import CustomUser

# Custom form to filter only shop_owner users
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['shop_owner'].queryset = CustomUser.objects.filter(role='shop_owner')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ['name', 'price', 'shop_owner']
