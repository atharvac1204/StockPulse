import requests
import json
import time

# Test the manual suggestion endpoints
print("Testing manual suggestion endpoints...")

# First, get a product
response = requests.get("http://localhost:8000/products")
if response.status_code == 200:
    products = response.json()
    if products:
        product_id = products[0]['id']
        print(f"Found product with ID: {product_id}")
        
        # Test manual pricing suggestion
        response = requests.post(f"http://localhost:8000/products/{product_id}/suggest-pricing")
        print(f"Pricing suggestion status: {response.status_code}")
        if response.status_code == 200:
            print(f"Pricing suggestion: {response.json()}")
        else:
            print(f"Pricing suggestion failed: {response.text}")
        
        # Test manual reorder suggestion
        response = requests.post(f"http://localhost:8000/products/{product_id}/suggest-reorder")
        print(f"Reorder suggestion status: {response.status_code}")
        if response.status_code == 200:
            print(f"Reorder suggestion: {response.json()}")
        else:
            print(f"Reorder suggestion failed: {response.text}")
        
        # Test creating persistent suggestions
        pricing_data = {
            "product_id": product_id,
            "current_price": 29.99,
            "recommended_price": 32.99,
            "direction": "INCREASE",
            "confidence": 0.9,
            "reasoning": "Low stock detected",
            "trigger_reason": "MANUAL"
        }
        
        response = requests.post("http://localhost:8000/suggestions/pricing", json=pricing_data)
        print(f"Create pricing suggestion status: {response.status_code}")
        if response.status_code == 201:
            pricing_suggestion = response.json()
            print(f"Pricing suggestion created: {pricing_suggestion}")
            
            # Test accepting the suggestion
            accept_data = {"status": "ACCEPTED"}
            response = requests.patch(f"http://localhost:8000/suggestions/pricing/{pricing_suggestion['id']}", json=accept_data)
            print(f"Accept pricing suggestion status: {response.status_code}")
            if response.status_code == 200:
                print(f"Pricing suggestion accepted: {response.json()}")
            else:
                print(f"Failed to accept pricing suggestion: {response.text}")
        else:
            print(f"Failed to create pricing suggestion: {response.text}")
        
        # Test reorder suggestion
        reorder_data = {
            "product_id": product_id,
            "current_stock": 10,
            "recommended_quantity": 20,
            "lead_time": 3,
            "confidence": 0.85,
            "reasoning": "Low stock detected",
            "trigger_reason": "MANUAL"
        }
        
        response = requests.post("http://localhost:8000/suggestions/reorder", json=reorder_data)
        print(f"Create reorder suggestion status: {response.status_code}")
        if response.status_code == 201:
            reorder_suggestion = response.json()
            print(f"Reorder suggestion created: {reorder_suggestion}")
            
            # Test accepting the suggestion
            accept_data = {"status": "ACCEPTED"}
            response = requests.patch(f"http://localhost:8000/suggestions/reorder/{reorder_suggestion['id']}", json=accept_data)
            print(f"Accept reorder suggestion status: {response.status_code}")
            if response.status_code == 200:
                print(f"Reorder suggestion accepted: {response.json()}")
            else:
                print(f"Failed to accept reorder suggestion: {response.text}")
        else:
            print(f"Failed to create reorder suggestion: {response.text}")
            
    else:
        print("No products found")
else:
    print(f"Failed to get products: {response.status_code}")

# Test getting suggestions
print("\nTesting get suggestions...")
response = requests.get("http://localhost:8000/suggestions/pricing")
if response.status_code == 200:
    print(f"Pricing suggestions: {response.json()}")
else:
    print(f"Failed to get pricing suggestions: {response.status_code}")

response = requests.get("http://localhost:8000/suggestions/reorder")
if response.status_code == 200:
    print(f"Reorder suggestions: {response.json()}")
else:
    print(f"Failed to get reorder suggestions: {response.status_code}")