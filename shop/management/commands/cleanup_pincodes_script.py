import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'localshop.settings')
django.setup()

from shop.models import PinCode
from shop.utils.pincode_utils import fetch_pincode_data

def run_cleanup():
    print("🚀 Starting Pincode Cleanup...")
    pincodes = PinCode.objects.all()
    count = 0
    
    for p in pincodes:
        # Check if record needs fixing
        if not p.city or (p.area_name and p.area_name.startswith("Pincode")):
            print(f"🔍 Checking {p.code}...")
            area, city = fetch_pincode_data(p.code)
            
            if area:
                p.area_name = area
                p.city = city
                p.is_auto_created = False
                p.save()
                count += 1
                print(f"✅ Fixed {p.code}: {area}, {city}")
            else:
                print(f"⚠️ Could not resolve {p.code} via API.")
                
    print(f"🏆 Cleanup finished. Fixed {count} records.")

if __name__ == "__main__":
    run_cleanup()
