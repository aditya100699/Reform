#!/usr/bin/env python
"""
Database initialization script.
Run this after setting up the database to create initial data.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reform.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Provider

User = get_user_model()

def create_sample_providers():
    """Create sample healthcare providers for testing."""
    providers = [
        {
            'name': 'Apollo Hospitals',
            'provider_type': Provider.ProviderType.HOSPITAL,
            'registration_number': 'APL001',
            'email': 'contact@apollohospitals.com',
            'phone': '+91-11-12345678',
            'address': 'Sarita Vihar, New Delhi',
            'city': 'New Delhi',
            'state': 'Delhi',
            'pincode': '110076',
            'is_verified': True,
        },
        {
            'name': 'Max Healthcare',
            'provider_type': Provider.ProviderType.HOSPITAL,
            'registration_number': 'MAX001',
            'email': 'info@maxhealthcare.com',
            'phone': '+91-11-23456789',
            'address': 'Saket, New Delhi',
            'city': 'New Delhi',
            'state': 'Delhi',
            'pincode': '110017',
            'is_verified': True,
        },
        {
            'name': 'Apollo Diagnostics',
            'provider_type': Provider.ProviderType.LAB,
            'registration_number': 'APLDIAG001',
            'email': 'info@apollodiagnostics.com',
            'phone': '+91-11-34567890',
            'address': 'Multiple Locations',
            'city': 'New Delhi',
            'state': 'Delhi',
            'pincode': '110001',
            'is_verified': True,
        },
    ]
    
    for provider_data in providers:
        provider, created = Provider.objects.get_or_create(
            registration_number=provider_data['registration_number'],
            defaults=provider_data
        )
        if created:
            print(f"Created provider: {provider.name}")
        else:
            print(f"Provider already exists: {provider.name}")

if __name__ == '__main__':
    print("Initializing database...")
    create_sample_providers()
    print("Database initialization complete!")

