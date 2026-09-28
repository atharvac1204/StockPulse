import requests
import json

# Test the order endpoint
print("Testing order endpoint...")

# First, get a product
response = requests.get("http://localhost:8000/products")
if response.status_code == 200:
    products = response.json()
    if products:
        product_id = products[0]['id']
        print(f"Found product with ID: {product_id}")
        
        # Test creating an order
        order_data = {"quantity": 1}
        response = requests.post(f"http://localhost:8000/products/{product_id}/orders", json=order_data)
        print(f"Order response status: {response.status_code}")
        if response.status_code == 200:
            print(f"Order created successfully: {response.json()}")
        else:
            print(f"Order creation failed: {response.text}")
    else:
        print("No products found")
else:
    print(f"Failed to get products: {response.status_code}")

# Test the stock update endpoint
print("\nTesting stock update endpoint...")

# Get a product
response = requests.get("http://localhost:8000/products")
if response.status_code == 200:
    products = response.json()
    if products:
        product_id = products[0]['id']
        print(f"Found product with ID: {product_id}")
        
        # Test updating stock
        stock_data = {"stock_level": 15}
        response = requests.patch(f"http://localhost:8000/products/{product_id}/stock", json=stock_data)
        print(f"Stock update response status: {response.status_code}")
        if response.status_code == 200:
            print(f"Stock updated successfully: {response.json()}")
        else:
            print(f"Stock update failed: {response.text}")
    else:
        print("No products found")
else:
    print(f"Failed to get products: {response.status_code}")

# Test pricing recommendation
print("\nTesting pricing recommendation...")
response = requests.get("http://localhost:8000/products")
if response.status_code == 200:
    products = response.json()
    if products:
        product_id = products[0]['id']
        response = requests.get(f"http://localhost:8000/products/{product_id}/pricing")
        print(f"Pricing recommendation status: {response.status_code}")
        if response.status_code == 200:
            print(f"Pricing recommendation: {response.json()}")
        else:
            print(f"Pricing recommendation failed: {response.text}")

# Test reorder recommendation
print("\nTesting reorder recommendation...")
response = requests.get("http://localhost:8000/products")
if response.status_code == 200:
    products = response.json()
    if products:
        product_id = products[0]['id']
        response = requests.get(f"http://localhost:8000/products/{product_id}/reorder")
        print(f"Reorder recommendation status: {response.status_code}")
        if response.status_code == 200:
            print(f"Reorder recommendation: {response.json()}")
        else:
            print(f"Reorder recommendation failed: {response.text}")