from django.contrib import admin
from django import forms
from users.models import CustomUser
from .models import Product, Category, PinCode, Invoice, Payment
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

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'order', 'total_amount', 'payment_status', 'generated_date']
    list_filter = ['payment_status', 'generated_date']
    search_fields = ['invoice_number', 'order__id', 'order__customer__email']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'order', 'payment_method', 'amount', 'payment_status', 'payment_date']
    list_filter = ['payment_method', 'payment_status', 'payment_date']
    search_fields = ['transaction_id', 'order__id', 'order__customer__email']
    
    actions = ['mark_as_completed', 'mark_as_pending', 'mark_as_failed']
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(payment_status='completed')
        # Update related invoices
        for payment in queryset:
            if payment.invoice:
                payment.invoice.payment_status = 'paid'
                payment.invoice.save()
        self.message_user(request, f'{updated} payments marked as completed.')
    mark_as_completed.short_description = "Mark selected payments as completed"
    
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(payment_status='pending')
        self.message_user(request, f'{updated} payments marked as pending.')
    mark_as_pending.short_description = "Mark selected payments as pending"
    
    def mark_as_failed(self, request, queryset):
        updated = queryset.update(payment_status='failed')
        self.message_user(request, f'{updated} payments marked as failed.')
    mark_as_failed.short_description = "Mark selected payments as failed"
