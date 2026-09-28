#!/usr/bin/env python3
"""
Simple verification script to check database contents
"""

import sys
import os

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import SessionLocal
from models import Product

def check_database_contents():
    """Check what's in the database."""
    db = SessionLocal()
    try:
        # Count total products
        total_products = db.query(Product).count()
        print(f"📊 Total products in database: {total_products}")
        
        # List all products
        products = db.query(Product).all()
        print("\n📦 All products:")
        for product in products:
            print(f"  - {product.sku}: {product.name} (Stock: {product.stock_level}, Status: {product.status})")
        
        return total_products
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return 0
    finally:
        db.close()

if __name__ == "__main__":
    print("🔍 Checking database contents...")
    count = check_database_contents()
    print(f"\n✅ Database check complete. Found {count} products.")