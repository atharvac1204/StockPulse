#!/usr/bin/env python3
"""
Test script for StockPulse seed functionality.
Verifies that the seed script works correctly and is idempotent.
"""

import sys
import os

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import SessionLocal
from models import Product

def count_products():
    """Count the total number of products in the database."""
    db = SessionLocal()
    try:
        count = db.query(Product).count()
        return count
    finally:
        db.close()

def get_product_by_sku(sku):
    """Get a product by SKU."""
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.sku == sku).first()
        return product
    finally:
        db.close()

def test_seed_idempotency():
    """Test that the seed script is idempotent."""
    print("🧪 Testing seed script idempotency...")
    
    # Import and run seed script
    import seed
    
    # Run seed script first time
    print("\n📝 Running seed script - First time...")
    first_run_count = seed.seed_products()
    total_after_first = count_products()
    
    print(f"📊 Products after first run: {total_after_first}")
    
    # Run seed script second time
    print("\n📝 Running seed script - Second time (idempotency test)...")
    second_run_count = seed.seed_products()
    total_after_second = count_products()
    
    print(f"📊 Products after second run: {total_after_second}")
    
    # Verify idempotency
    if total_after_first == total_after_second:
        print("✅ Idempotency test passed - no duplicates created")
        return True
    else:
        print(f"❌ Idempotency test failed - expected {total_after_first} products, got {total_after_second}")
        return False

def test_specific_product_requirements():
    """Test the specific product requirements from the brief."""
    print("\n🧪 Testing specific product requirements...")
    
    # Test PRD-003 T-Shirt
    prd_003 = get_product_by_sku("PRD-003")
    if prd_003:
        print("✅ PRD-003 T-Shirt found")
        tests_passed = True
        
        # Verify name
        if prd_003.name == "T-Shirt":
            print("✅ PRD-003 name is correct")
        else:
            print(f"❌ PRD-003 name incorrect: expected 'T-Shirt', got '{prd_003.name}'")
            tests_passed = False
            
        # Verify stock_level
        if prd_003.stock_level == 8:
            print("✅ PRD-003 stock_level is correct (8)")
        else:
            print(f"❌ PRD-003 stock_level incorrect: expected 8, got {prd_003.stock_level}")
            tests_passed = False
            
        # Verify reorder_threshold
        if prd_003.reorder_threshold == 15:
            print("✅ PRD-003 reorder_threshold is correct (15)")
        else:
            print(f"❌ PRD-003 reorder_threshold incorrect: expected 15, got {prd_003.reorder_threshold}")
            tests_passed = False
    else:
        print("❌ PRD-003 T-Shirt not found")
        tests_passed = False
    
    # Test PRD-008 Hoodie
    prd_008 = get_product_by_sku("PRD-008")
    if prd_008:
        print("✅ PRD-008 Hoodie found")
        
        # Verify name
        if prd_008.name == "Hoodie":
            print("✅ PRD-008 name is correct")
        else:
            print(f"❌ PRD-008 name incorrect: expected 'Hoodie', got '{prd_008.name}'")
            tests_passed = False
            
        # Verify stock_level
        if prd_008.stock_level == 11:
            print("✅ PRD-008 stock_level is correct (11)")
        else:
            print(f"❌ PRD-008 stock_level incorrect: expected 11, got {prd_008.stock_level}")
            tests_passed = False
            
        # Verify reorder_threshold
        if prd_008.reorder_threshold == 12:
            print("✅ PRD-008 reorder_threshold is correct (12)")
        else:
            print(f"❌ PRD-008 reorder_threshold incorrect: expected 12, got {prd_008.reorder_threshold}")
            tests_passed = False
            
        # Verify demand_velocity
        if prd_008.demand_velocity == 15:
            print("✅ PRD-008 demand_velocity is correct (15)")
        else:
            print(f"❌ PRD-008 demand_velocity incorrect: expected 15, got {prd_008.demand_velocity}")
            tests_passed = False
    else:
        print("❌ PRD-008 Hoodie not found")
        tests_passed = False
    
    return tests_passed
def test_sku_uniqueness():
    """Test that all SKUs are unique."""
    print("\n🧪 Testing SKU uniqueness...")
    
    db = SessionLocal()
    try:
        # Get all SKUs
        skus = db.query(Product.sku).all()
        sku_list = [sku[0] for sku in skus]
        
        # Check for duplicates
        unique_skus = set(sku_list)
        if len(sku_list) == len(unique_skus):
            print(f"✅ All {len(sku_list)} SKUs are unique")
            return True
        else:
            duplicates = [sku for sku in sku_list if sku_list.count(sku) > 1]
            print(f"❌ Duplicate SKUs found: {set(duplicates)}")
            return False
    finally:
        db.close()

def test_product_status_rules():
    """Test that product status rules are followed."""
    print("\n🧪 Testing product status rules...")
    
    db = SessionLocal()
    try:
        # Get all products
        products = db.query(Product).all()
        
        status_correct = True
        for product in products:
            if product.stock_level == 0:
                if product.status != "OUT_OF_STOCK":
                    print(f"❌ Product {product.sku} has stock_level 0 but status {product.status} (should be OUT_OF_STOCK)")
                    status_correct = False
            else:
                if product.status != "ACTIVE":
                    print(f"❌ Product {product.sku} has stock_level {product.stock_level} but status {product.status} (should be ACTIVE)")
                    status_correct = False
        
        if status_correct:
            print("✅ All product status rules are correct")
            return True
        else:
            return False
    finally:
        db.close()

def test_total_product_count():
    """Test that exactly 8 products exist."""
    print("\n🧪 Testing total product count...")
    
    count = count_products()
    if count == 8:
        print("✅ Exactly 8 products exist")
        return True
    else:
        print(f"❌ Expected 8 products, found {count}")
        return False

if __name__ == "__main__":
    print("🚀 Running StockPulse seed tests...")
    print("=" * 50)
    
    # Run all tests
    tests = [
        ("Total Product Count", test_total_product_count),
        ("Seed Idempotency", test_seed_idempotency),
        ("Specific Product Requirements", test_specific_product_requirements),
        ("SKU Uniqueness", test_sku_uniqueness),
        ("Product Status Rules", test_product_status_rules),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n{name}:")
        try:
            if test_func():
                passed += 1
                print(f"✅ {name} PASSED")
            else:
                print(f"❌ {name} FAILED")
        except Exception as e:
            print(f"❌ {name} ERROR: {e}")
    
    print(f"\n{'='*50}")
    print(f"FINAL RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All seed tests passed!")
        print("\n📋 Summary:")
        print("  - ✅ Exactly 8 products seeded")
        print("  - ✅ Seed script is idempotent (no duplicates)")
        print("  - ✅ PRD-003 T-Shirt has correct values")
        print("  - ✅ PRD-008 Hoodie has correct values")
        print("  - ✅ All SKUs are unique")
        print("  - ✅ Product status rules are enforced")
    else:
        print("💥 Some seed tests failed!")
        sys.exit(1)