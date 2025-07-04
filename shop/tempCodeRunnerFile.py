class ShopBankInfo(models.Model):
    PAYMENT_CHOICES = [
        ('bank', 'Bank Transfer'),
        ('upi', 'UPI'),
        ('both', 'Both'),
    ]

    shop = models.OneToOneField('Shop', on_delete=models.CASCADE)
    
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='bank')  # ✅ NEW FIELD

    account_holder_name = models.CharField(max_length=255, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    logo = models.ImageField(upload_to='shop_logos/', null=True, blank=True)

    upi_id = models.CharField(max_length=100, blank=True, null=True)
    PREFERRED_CHOICES = [
        ('bank', 'Bank Transfer'),
        ('upi', 'UPI'),
        ('both', 'Both'),
    ]

    def __str__(self):
        return f"{self.shop.shop_name} - Bank Info"