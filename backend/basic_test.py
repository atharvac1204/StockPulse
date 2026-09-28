import requests
import os

BASE_URL = "http://localhost:8000"

def test_basic_endpoints():
    print("Testing basic endpoints...")
    
    # Test health endpoint
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health endpoint: {response.status_code}")
    
    # Test products endpoint
    response = requests.get(f"{BASE_URL}/products")
    print(f"Products endpoint: {response.status_code}")
    
    # Test suggestions endpoints
    response = requests.get(f"{BASE_URL}/suggestions/pricing")
    print(f"Pricing suggestions endpoint: {response.status_code}")
    
    response = requests.get(f"{BASE_URL}/suggestions/reorder")
    print(f"Reorder suggestions endpoint: {response.status_code}")

def test_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"GEMINI_API_KEY configured: {'Yes' if api_key else 'No'}")

if __name__ == "__main__":
    test_basic_endpoints()
    test_gemini()