from django.contrib import admin
from django import forms
from users.models import CustomUser
from .models import Product, Category, PinCode
admin.site.register(Category)

# Custom form to filter only shop_owner users
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['shop_owner'].queryset = CustomUser.objects.filter(role='shop_owner')

@admin.register(PinCode)
class PinCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'area_name')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ['name', 'price', 'shop_owner']
