import os
import sys
import django
from datetime import date, timedelta

# Ensure script is run from project root
if not os.path.exists('manage.py'):
    print('Run this script from your Django project root (where manage.py is located).')
    sys.exit(1)

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ClinicNet0.settings')
django.setup()

from pharmacy.models import Product, Category, MedicineBatch

# Sample categories
categories = [
    'Analgesic', 'Antibiotic', 'Antihistamine', 'Antacid', 'Antipyretic', 'Antiseptic', 'Cough Suppressant', 'Vitamin', 'Antifungal', 'Antiviral'
]

category_objs = {}
for cat in categories:
    obj, _ = Category.objects.get_or_create(name=cat)
    category_objs[cat] = obj

# Sample medicines and batches
medicines = [
    {
        'name': 'Paracetamol 500mg',
        'category': 'Antipyretic',
        'unit_price': 20,
        'batches': [
            {'batch_number': 'PCT2024A', 'mfg': date(2024, 5, 1), 'exp': date(2026, 5, 1), 'quantity': 200},
        ]
    },
    {
        'name': 'Amoxicillin 250mg',
        'category': 'Antibiotic',
        'unit_price': 60,
        'batches': [
            {'batch_number': 'AMX2024B', 'mfg': date(2024, 3, 15), 'exp': date(2025, 9, 15), 'quantity': 120},
        ]
    },
    {
        'name': 'Cetirizine 10mg',
        'category': 'Antihistamine',
        'unit_price': 30,
        'batches': [
            {'batch_number': 'CTR2024C', 'mfg': date(2024, 6, 10), 'exp': date(2026, 6, 10), 'quantity': 150},
        ]
    },
    {
        'name': 'Omeprazole 20mg',
        'category': 'Antacid',
        'unit_price': 50,
        'batches': [
            {'batch_number': 'OMP2024D', 'mfg': date(2024, 2, 20), 'exp': date(2025, 8, 20), 'quantity': 100},
        ]
    },
    {
        'name': 'Ibuprofen 400mg',
        'category': 'Analgesic',
        'unit_price': 40,
        'batches': [
            {'batch_number': 'IBU2024E', 'mfg': date(2024, 4, 5), 'exp': date(2026, 4, 5), 'quantity': 180},
        ]
    },
    {
        'name': 'Vitamin C 500mg',
        'category': 'Vitamin',
        'unit_price': 25,
        'batches': [
            {'batch_number': 'VIT2024F', 'mfg': date(2024, 7, 1), 'exp': date(2026, 7, 1), 'quantity': 220},
        ]
    },
    {
        'name': 'Fluconazole 150mg',
        'category': 'Antifungal',
        'unit_price': 90,
        'batches': [
            {'batch_number': 'FLU2024G', 'mfg': date(2024, 1, 10), 'exp': date(2025, 7, 10), 'quantity': 80},
        ]
    },
    {
        'name': 'Acyclovir 400mg',
        'category': 'Antiviral',
        'unit_price': 100,
        'batches': [
            {'batch_number': 'ACY2024H', 'mfg': date(2024, 3, 25), 'exp': date(2025, 9, 25), 'quantity': 60},
        ]
    },
    {
        'name': 'Chlorhexidine Solution',
        'category': 'Antiseptic',
        'unit_price': 70,
        'batches': [
            {'batch_number': 'CHX2024I', 'mfg': date(2024, 5, 15), 'exp': date(2026, 5, 15), 'quantity': 90},
        ]
    },
    {
        'name': 'Dextromethorphan Syrup',
        'category': 'Cough Suppressant',
        'unit_price': 55,
        'batches': [
            {'batch_number': 'DXM2024J', 'mfg': date(2024, 6, 20), 'exp': date(2026, 6, 20), 'quantity': 110},
        ]
    },
]

for med in medicines:
    product, _ = Product.objects.get_or_create(
        item_name=med['name'],
        category_name=category_objs[med['category']],
        defaults={'unit_price': med['unit_price']}
    )
    product.unit_price = med['unit_price']
    product.save()
    for batch in med['batches']:
        MedicineBatch.objects.get_or_create(
            product=product,
            batch_number=batch['batch_number'],
            manufacture_date=batch['mfg'],
            expiry_date=batch['exp'],
            quantity=batch['quantity']
        )

print('Sample pharmacy inventory populated.') 