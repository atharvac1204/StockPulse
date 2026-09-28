#!/usr/bin/env python3
"""
Quick test for StockPulse seed requirements.
"""

import sys
import os

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import SessionLocal
from models import Product

def quick_test():
    """Quick test of seed requirements."""
    print("🧪 Quick testing StockPulse seed requirements...")
    
    db = SessionLocal()
    try:
        # Count products
        total = db.query(Product).count()
        print(f"📊 Total products: {total}")
        
        # Check PRD-003
        prd_003 = db.query(Product).filter(Product.sku == "PRD-003").first()
        if prd_003:
            print(f"✅ PRD-003: {prd_003.name}")
            print(f"   Stock: {prd_003.stock_level} (expected: 8)")
            print(f"   Threshold: {prd_003.reorder_threshold} (expected: 15)")
        
        # Check PRD-008
        prd_008 = db.query(Product).filter(Product.sku == "PRD-008").first()
        if prd_008:
            print(f"✅ PRD-008: {prd_008.name}")
            print(f"   Stock: {prd_008.stock_level} (expected: 11)")
            print(f"   Threshold: {prd_008.reorder_threshold} (expected: 12)")
            print(f"   Velocity: {prd_008.demand_velocity} (expected: 15)")
        
        # Check status rules
        out_of_stock = db.query(Product).filter(Product.status == "OUT_OF_STOCK").all()
        print(f"✅ Out of stock products: {len(out_of_stock)}")
        for p in out_of_stock:
            print(f"   - {p.sku}: stock {p.stock_level}")
        
        # Check SKU uniqueness
        skus = db.query(Product.sku).all()
        sku_list = [sku[0] for sku in skus]
        if len(sku_list) == len(set(sku_list)):
            print(f"✅ All {len(sku_list)} SKUs are unique")
        else:
            print("❌ Duplicate SKUs found")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    quick_test()