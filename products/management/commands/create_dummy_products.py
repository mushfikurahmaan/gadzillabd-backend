"""
Management command to create 100 dummy products across all categories.
"""
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from products.models import Category, Product


# Product name templates for each subcategory
PRODUCT_TEMPLATES = {
    # Gadgets subcategories
    'new': [
        '{brand} Latest Smart Device',
        '{brand} Next-Gen Gadget Pro',
        '{brand} Innovation Hub',
        '{brand} Future Tech Device',
        '{brand} Smart Connect Pro',
    ],
    'audio': [
        '{brand} Wireless Headphones',
        '{brand} Bluetooth Speaker',
        '{brand} Noise Cancelling Earbuds',
        '{brand} Studio Monitor',
        '{brand} Soundbar Pro',
        '{brand} Portable Speaker',
        '{brand} Gaming Headset',
        '{brand} True Wireless Earphones',
    ],
    'wearables': [
        '{brand} Smartwatch Pro',
        '{brand} Fitness Tracker',
        '{brand} Smart Band',
        '{brand} Health Monitor Watch',
        '{brand} Sport Watch',
        '{brand} Smart Ring',
        '{brand} GPS Running Watch',
    ],
    'smart-home': [
        '{brand} Smart Hub',
        '{brand} WiFi Router Pro',
        '{brand} Smart Light Bulb',
        '{brand} Video Doorbell',
        '{brand} Smart Thermostat',
        '{brand} Security Camera',
        '{brand} Smart Plug',
        '{brand} Voice Assistant',
    ],
    'gaming': [
        '{brand} Gaming Controller',
        '{brand} Gaming Mouse',
        '{brand} Mechanical Keyboard',
        '{brand} Gaming Monitor',
        '{brand} VR Headset',
        '{brand} Streaming Deck',
        '{brand} Gaming Chair',
    ],
    'cameras': [
        '{brand} Mirrorless Camera',
        '{brand} Action Camera',
        '{brand} Instant Camera',
        '{brand} Webcam Pro',
        '{brand} Security Cam',
        '{brand} Dash Cam',
        '{brand} 360 Camera',
    ],
    'drones': [
        '{brand} Quadcopter Pro',
        '{brand} Mini Drone',
        '{brand} Racing Drone',
        '{brand} Camera Drone',
        '{brand} FPV Drone Kit',
        '{brand} Aerial Photography Drone',
    ],
    # Accessories subcategories
    'accessories-new': [
        '{brand} Latest Accessory Kit',
        '{brand} Premium Accessory Pack',
        '{brand} New Arrival Bundle',
        '{brand} Trending Accessory',
    ],
    'chargers': [
        '{brand} Fast Charger 65W',
        '{brand} Wireless Charging Pad',
        '{brand} USB-C Charger',
        '{brand} Car Charger Dual Port',
        '{brand} MagSafe Charger',
        '{brand} GaN Charger 100W',
        '{brand} Desktop Charging Station',
    ],
    'cables': [
        '{brand} USB-C Cable 2m',
        '{brand} Lightning Cable',
        '{brand} HDMI 2.1 Cable',
        '{brand} Braided Charging Cable',
        '{brand} Fast Charging Cable',
        '{brand} Multi-Port Cable',
        '{brand} Thunderbolt 4 Cable',
    ],
    'stands': [
        '{brand} Laptop Stand',
        '{brand} Phone Holder',
        '{brand} Tablet Mount',
        '{brand} Monitor Arm',
        '{brand} Desk Stand Pro',
        '{brand} Car Phone Mount',
        '{brand} Adjustable Stand',
    ],
    'power-bank': [
        '{brand} Power Bank 20000mAh',
        '{brand} Slim Power Bank 10000mAh',
        '{brand} Solar Power Bank',
        '{brand} Fast Charging Power Bank',
        '{brand} Wireless Power Bank',
        '{brand} Laptop Power Bank 30000mAh',
        '{brand} Mini Power Bank 5000mAh',
    ],
}

BRANDS = [
    'TechPro', 'Nexus', 'Zenith', 'Quantum', 'Apex',
    'Stellar', 'Vortex', 'Pulse', 'Echo', 'Nova',
    'Orion', 'Atlas', 'Phoenix', 'Titan', 'Vertex',
]

DESCRIPTIONS = [
    'Premium quality product designed for everyday use. Features cutting-edge technology and sleek design.',
    'Experience the next level of innovation with this state-of-the-art device. Built to last and perform.',
    'Elevate your tech experience with this premium product. Crafted with precision and attention to detail.',
    'The perfect blend of style and functionality. Designed for those who demand the best.',
    'High-performance product that delivers exceptional results. Your perfect companion for modern life.',
    'Innovative design meets reliable performance. A must-have for tech enthusiasts.',
    'Compact yet powerful. This product punches above its weight in every category.',
    'Engineered for excellence. Superior build quality and outstanding performance.',
]

BADGES = [None, None, None, 'sale', 'new', 'hot']  # More None for variety


class Command(BaseCommand):
    help = 'Creates 100 dummy products across all categories'

    def handle(self, *args, **options):
        # Get all categories
        main_categories = Category.objects.filter(parent__isnull=True, is_active=True)
        subcategories = Category.objects.filter(parent__isnull=False, is_active=True)
        
        if not subcategories.exists():
            self.stdout.write(self.style.ERROR('No subcategories found. Run migrations first.'))
            return
        
        self.stdout.write(f'Found {subcategories.count()} subcategories')
        
        # Calculate products per subcategory (distribute 100 products)
        subcat_list = list(subcategories)
        products_per_subcat = 100 // len(subcat_list)
        extra_products = 100 % len(subcat_list)
        
        created_count = 0
        product_number = 1
        
        for i, subcat in enumerate(subcat_list):
            # Add extra product to first few subcategories if needed
            num_products = products_per_subcat + (1 if i < extra_products else 0)
            main_cat = subcat.parent
            
            # Get product templates for this subcategory
            templates = PRODUCT_TEMPLATES.get(subcat.slug, PRODUCT_TEMPLATES.get('new', ['{brand} Product']))
            
            for j in range(num_products):
                brand = random.choice(BRANDS)
                template = templates[j % len(templates)]
                name = template.format(brand=brand)
                
                # Add variant suffix if we have duplicate names
                if j >= len(templates):
                    name += f' {["Pro", "Plus", "Max", "Ultra", "Lite", "SE", "X"][j % 7]}'
                
                # Generate unique slug
                base_slug = slugify(name)
                slug = f'{base_slug}-{product_number}'
                
                # Random price between 19.99 and 999.99
                price = Decimal(random.randint(1999, 99999)) / 100
                
                # Sometimes add original price (for sale items)
                badge = random.choice(BADGES)
                original_price = None
                if badge == 'sale':
                    # Original price is 10-40% higher
                    markup = Decimal(random.randint(110, 140)) / 100
                    original_price = (price * markup).quantize(Decimal('0.01'))
                
                # Create the product
                Product.objects.create(
                    name=name,
                    brand=brand,
                    slug=slug,
                    price=price,
                    original_price=original_price,
                    badge=badge,
                    category=main_cat,
                    sub_category=subcat,
                    description=random.choice(DESCRIPTIONS),
                    is_featured=random.random() < 0.15,  # 15% chance of being featured
                    is_active=True,
                )
                
                created_count += 1
                product_number += 1
            
            self.stdout.write(f'  Created {num_products} products in {main_cat.name} > {subcat.name}')
        
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {created_count} dummy products!'))
        
        # Print summary
        self.stdout.write('\nSummary by category:')
        for main_cat in main_categories:
            count = Product.objects.filter(category=main_cat).count()
            self.stdout.write(f'  {main_cat.name}: {count} products')
            for subcat in main_cat.children.filter(is_active=True):
                sub_count = Product.objects.filter(sub_category=subcat).count()
                self.stdout.write(f'    - {subcat.name}: {sub_count} products')
