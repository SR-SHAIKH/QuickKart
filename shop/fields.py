import re
from django import forms
from .models import PinCode
from shop.utils.pincode_utils import fetch_pincode_data

class DeliveryPinCodeField(forms.ModelMultipleChoiceField):
    def clean(self, value):
        if not value:
            return []

        pincodes = []
        for val in value:
            # Cleanup and validation
            val = val.strip()
            if not re.match(r'^\d{6}$', val):
                continue  # Skip invalid 6-digit pincode entries
            
            # 🔥 API Lookup
            area, city = fetch_pincode_data(val)
            print(f"PIN: {val} AREA: {area} CITY: {city}") # DEBUG LOG

            # 🌍 Handle Global Codes manually if needed (Metadata only)
            if val in ['000000', '111111']:
                area, city = 'Global Delivery', 'All India'

            # 1. Check for existing pincode object
            obj, created = PinCode.objects.get_or_create(
                code=val,
                defaults={
                    'area_name': area or f"Pincode {val}",
                    'city': city or '',
                    'is_auto_created': not bool(area)
                }
            )
            
            # 🔥 CRITICAL FIX: Update existing records if they have placeholders or missing city
            if not created:
                if (not obj.city or obj.area_name.startswith("Pincode")) and area:
                    obj.area_name = area
                    obj.city = city
                    if area: # If we got real data, it's no longer just an "auto" placeholder
                        obj.is_auto_created = False
                    obj.save()
            
            pincodes.append(obj)

        return pincodes
