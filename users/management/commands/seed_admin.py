import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Automatically seeds the Superuser specifically configured via local/remote Environment Variables'

    def handle(self, *args, **kwargs):
        # 1. Load context model
        User = get_user_model()

        # 2. Extract values securely
        email = os.getenv("ADMIN_EMAIL")
        password = os.getenv("ADMIN_PASSWORD")
        role = os.getenv("ADMIN_ROLE", "admin")  # Defaulting as per Requirement 3 constraint

        # 3. Explicit Validation Requirement 
        if not email or not password:
            self.stdout.write(self.style.ERROR("Missing environment variables"))
            raise CommandError("Required ADMIN_EMAIL or ADMIN_PASSWORD secrets are missing from the OS environment.")

        # 4 & 5. Idempotent check
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING("Admin already exists"))
            return

        # 6. Instantiate the payload via create_superuser to inherit automatic cryptographic hashing parameters
        try:
            # CustomUser specifically mandates email authentication mapping fields
            admin = User.objects.create_superuser(
                email=email,
                password=password,
                role=role  # Pass any dynamically instantiated explicit fields
            )
            # 4. Success Logging stringency 
            self.stdout.write(self.style.SUCCESS("Admin created successfully"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Critical execution error generating database superuser: {e}"))
            raise e
