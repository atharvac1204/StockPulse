#!/usr/bin/env python3
"""
Direct seed script for StockPulse demo products.
"""

import sys
import os

# Add the parent directory to Python path so we can import backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import Product, ProductStatusEnum

def seed_demo_products():
    """Directly seed the 8 demo products."""
    db = SessionLocal()
    try:
        # Demo products from the hackathon brief
        demo_products = [
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
        
        seeded_count = 0
        
        for product_data in demo_products:
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

if __name__ == "__main__":
    print("🌱 Seeding StockPulse demo products...")
    print("=" * 50)
    seed_demo_products()