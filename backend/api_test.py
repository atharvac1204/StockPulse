#!/usr/bin/env python3
"""
Test to verify products can be retrieved through API.
"""

import sys
import os

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_api_retrieval():
    """Test that products can be retrieved through API."""
    try:
        import urllib.request
        import urllib.parse
        import json
        
        BASE_URL = "http://localhost:8000"
        
        def make_request(url, method='GET'):
            """Make an HTTP request"""
            req = urllib.request.Request(url, method=method)
            
            try:
                with urllib.request.urlopen(req) as response:
                    return response.getcode(), response.read().decode('utf-8')
            except urllib.error.HTTPError as e:
                return e.getcode(), e.read().decode('utf-8')
            except Exception as e:
                return None, str(e)
        
        # Test GET /products
        print("Testing GET /products...")
        code, response = make_request(f"{BASE_URL}/products/")
        if code == 200:
            data = json.loads(response)
            print(f"✅ GET /products returned {len(data)} products")
            
            # Look for our seeded products
            prd_003_found = any(p['sku'] == 'PRD-003' for p in data)
            prd_008_found = any(p['sku'] == 'PRD-008' for p in data)
            
            if prd_003_found:
                print("✅ PRD-003 found in API response")
            else:
                print("❌ PRD-003 not found in API response")
                
            if prd_008_found:
                print("✅ PRD-008 found in API response")
            else:
                print("❌ PRD-008 not found in API response")
                
            return prd_003_found and prd_008_found
        else:
            print(f"❌ GET /products failed with status {code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API retrieval: {e}")
        return False

if __name__ == "__main__":
    print("Testing API retrieval of seeded products...")
    if test_api_retrieval():
        print("\n✅ API retrieval test passed!")
    else:
        print("\n❌ API retrieval test failed!")