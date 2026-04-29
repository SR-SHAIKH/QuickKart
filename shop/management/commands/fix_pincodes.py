from django.core.management.base import BaseCommand
from shop.models import PinCode
from shop.utils.pincode_utils import fetch_pincode_data

class Command(BaseCommand):
    help = 'Retroactively fix pincode data by fetching real area and city names from the API'

    def handle(self, *args, **options):
        self.stdout.write("Starting Pincode Cleanup...")
        pincodes = PinCode.objects.all()
        count = 0
        
        for p in pincodes:
            # Check if record needs fixing
            if not p.city or (p.area_name and p.area_name.startswith("Pincode")):
                self.stdout.write(f"Checking {p.code}...")
                area, city = fetch_pincode_data(p.code)
                
                if area:
                    p.area_name = area
                    p.city = city
                    p.is_auto_created = False
                    p.save()
                    count += 1
                    self.stdout.write(self.style.SUCCESS(f"Fixed {p.code}: {area}, {city}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Could not resolve {p.code} via API."))
                    
        self.stdout.write(self.style.SUCCESS(f"Cleanup finished. Fixed {count} records."))
