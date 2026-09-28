#!/usr/bin/env python3
"""
Seed script for StockPulse demo products.
Creates the 8 demo products from the hackathon brief.
Idempotent - can be run multiple times without creating duplicates.
"""

import sys
import os

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Product, ProductStatusEnum

# Demo products from the hackathon brief
DEMO_PRODUCTS = [
    {
        "sku": "PRD-001",
        "name": "Wireless Earbuds Pro",
        "category": "ELECTRONICS",
        "current_price": 79.99,
        "stock_level": 45,
        "reorder_threshold": 20,
        "demand_velocity": 3
    },
    {
        "sku": "PRD-002", 
        "name": "USB-C Hub 7-Port",
        "category": "ELECTRONICS",
        "current_price": 34.99,
        "stock_level": 120,
        "reorder_threshold": 30,
        "demand_velocity": 1
    },
    {
        "sku": "PRD-003",
        "name": "T-Shirt",
        "category": "APPAREL",
        "current_price": 24.99,
        "stock_level": 8,           # From brief: stock 8
        "reorder_threshold": 15,    # From brief: threshold 15
        "demand_velocity": 12
    },
    {
        "sku": "PRD-004",
        "name": "Running Shorts — Navy",
        "category": "APPAREL",
        "current_price": 39.99,
        "stock_level": 55,
        "reorder_threshold": 20,
        "demand_velocity": 2
    },
    {
        "sku": "PRD-005",
        "name": "Ceramic Pour-Over Set",
        "category": "HOME",
def seed_products():
    """Seed the demo products into the database."""
    db = SessionLocal()
    try:
        seeded_count = 0
        
        for product_data in DEMO_PRODUCTS:
            # Check if product already exists
            existing_product = db.query(Product).filter(Product.sku == product_data["sku"]).first()
            
            if existing_product is None:
                # Set status based on stock level
                if product_data["stock_level"] == 0:
                    status = ProductStatusEnum.OUT_OF_STOCK.value
                else:
                    status = ProductStatusEnum.ACTIVE.value
                
                # Create new product
                product = Product(
                    sku=product_data["sku"],
                    name=product_data["name"],
                    category=product_data["category"],
                    current_price=product_data["current_price"],
                    stock_level=product_data["stock_level"],
                    reorder_threshold=product_data["reorder_threshold"],
                    demand_velocity=product_data["demand_velocity"],
                    status=status
                )
                
                db.add(product)
def verify_seeded_products():
    """Verify that all products were seeded correctly."""
    db = SessionLocal()
    try:
        # Count total products
        total_products = db.query(Product).count()
        print(f"\n📊 Total products in database: {total_products}")
        
        # Verify specific products
        prd_003 = db.query(Product).filter(Product.sku == "PRD-003").first()
        if prd_003:
            print(f"✅ PRD-003 T-Shirt verification:")
            print(f"   - Name: {prd_003.name}")
            print(f"   - Stock Level: {prd_003.stock_level} (expected: 8)")
            print(f"   - Reorder Threshold: {prd_003.reorder_threshold} (expected: 15)")
            print(f"   - Status: {prd_003.status}")
            
            # Verify values
            assert prd_003.name == "T-Shirt", f"Expected 'T-Shirt', got '{prd_003.name}'"
            assert prd_003.stock_level == 8, f"Expected stock_level 8, got {prd_003.stock_level}"
            assert prd_003.reorder_threshold == 15, f"Expected reorder_threshold 15, got {prd_003.reorder_threshold}"
        
        prd_008 = db.query(Product).filter(Product.sku == "PRD-008").first()
        if prd_008:
            print(f"✅ PRD-008 Hoodie verification:")
            print(f"   - Name: {prd_008.name}")
            print(f"   - Stock Level: {prd_008.stock_level} (expected: 11)")
            print(f"   - Reorder Threshold: {prd_008.reorder_threshold} (expected: 12)")
            print(f"   - Demand Velocity: {prd_008.demand_velocity} (expected: 15)")
            print(f"   - Status: {prd_008.status}")
            
            # Verify values
            assert prd_008.name == "Hoodie", f"Expected 'Hoodie', got '{prd_008.name}'"
            assert prd_008.stock_level == 11, f"Expected stock_level 11, got {prd_008.stock_level}"
            assert prd_008.reorder_threshold == 12, f"Expected reorder_threshold 12, got {prd_008.reorder_threshold}"
if __name__ == "__main__":
    print("🌱 Seeding StockPulse demo products...")
    print("=" * 50)
    
    try:
        # Seed products
        seeded_count = seed_products()
        
        # Verify products
        if verify_seeded_products():
            print("\n🎉 Seed script completed successfully!")
            print(f"📦 {seeded_count} new products were added to the database.")
        else:
            print("\n❌ Seed script completed but verification failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Seed script failed: {e}")
        sys.exit(1)
            assert prd_008.demand_velocity == 15, f"Expected demand_velocity 15, got {prd_008.demand_velocity}"
        
        # Verify status rules
        out_of_stock_products = db.query(Product).filter(Product.status == ProductStatusEnum.OUT_OF_STOCK.value).all()
        print(f"✅ Out of stock products: {len(out_of_stock_products)}")
        for product in out_of_stock_products:
            assert product.stock_level == 0, f"Product {product.sku} has status OUT_OF_STOCK but stock_level {product.stock_level}"
        
        # Verify SKU uniqueness
        skus = db.query(Product.sku).all()
        sku_list = [sku[0] for sku in skus]
        assert len(sku_list) == len(set(sku_list)), "Duplicate SKUs found!"
        print(f"✅ All {len(sku_list)} SKUs are unique")
        
        print("✅ All verifications passed!")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False
    finally:
        db.close()
                seeded_count += 1
                print(f"✅ Seeded product: {product_data['sku']} - {product_data['name']}")
            else:
                print(f"ℹ️  Product already exists: {product_data['sku']} - {product_data['name']}")
        
        db.commit()
        print(f"\n🎉 Seeding complete! {seeded_count} new products added.")
        return seeded_count
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding products: {e}")
        raise
    finally:
        db.close()
        "current_price": 49.99,
        "stock_level": 22,
        "reorder_threshold": 10,
        "demand_velocity": 4
    },
    {
        "sku": "PRD-006",
        "name": "LED Desk Lamp — Dimmable",
        "category": "HOME",
        "current_price": 59.99,
        "stock_level": 0,           # Should be OUT_OF_STOCK
        "reorder_threshold": 15,
        "demand_velocity": 0
    },
    {
        "sku": "PRD-007",
        "name": "Portable Charger 20K",
        "category": "ELECTRONICS",
        "current_price": 44.99,
        "stock_level": 18,
        "reorder_threshold": 25,
        "demand_velocity": 8
    },
    {
        "sku": "PRD-008",
        "name": "Hoodie",
        "category": "APPAREL",
        "current_price": 54.99,
        "stock_level": 11,          # From brief: stock 11
        "reorder_threshold": 12,    # From brief: threshold 12
        "demand_velocity": 15       # From brief: velocity 15
    }
]