#!/usr/bin/env bash

# Upgrade build tools
python -m pip install --upgrade pip setuptools

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --no-input

# Seed Superuser
python manage.py seed_admin


