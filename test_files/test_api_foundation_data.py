#!/usr/bin/env python3
"""
Test script for the updated API with foundation data integration.
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_api_with_foundation_data():
    """Test the API with foundation data."""
    print("🧪 Testing API with Foundation Data Integration")
    print("="*60)
    
    # Test data
    test_requests = [
        {
            "name": "Complete Foundation Data",
            "data": {
                "foundation_name": "Ford Foundation",
                "ein": "13-1684331",
                "foundation_contact": "info@fordfoundation.org",
                "foundation_address": "320 E 43rd St",
                "foundation_city": "New York, NY",
                "foundation_website_text": "fordfoundation.org",
                "prompt_variation": 4
            }
        },
        {
            "name": "Partial Foundation Data",
            "data": {
                "foundation_name": "William Penn Foundation",
                "foundation_address": "2 Logan Square",
                "foundation_city": "Philadelphia, PA",
                "prompt_variation": 4
            }
        },
        {
            "name": "Basic Request (No Data)",
            "data": {
                "foundation_name": "Gates Foundation"
            }
        }
    ]
    
    for test in test_requests:
        print(f"\n📋 Test: {test['name']}")
        print("-" * 40)
        
        try:
            # Make POST request
            response = requests.post(
                f"{API_BASE_URL}/find-foundation-url",
                json=test['data'],
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Status: {response.status_code}")
                print(f"📊 Foundation: {result['foundation_name']}")
                print(f"🔍 Search Provider: {result['search_provider']}")
                print(f"📝 Prompt Variation: {result.get('prompt_variation', 'N/A')}")
                print(f"📁 Foundation Data Used: {result.get('foundation_data_used', 'N/A')}")
                print(f"✅ Success: {result['success']}")
                print(f"💬 Message: {result['message']}")
                if result.get('url'):
                    print(f"🌐 URL: {result['url']}")
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"❌ Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Make sure the API server is running")
            print("   Start it with: python main.py")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_get_endpoint():
    """Test the GET endpoint with query parameters."""
    print(f"\n🔍 Testing GET Endpoint with Query Parameters")
    print("-" * 40)
    
    try:
        # Test GET with query parameters
        params = {
            "ein": "13-1684331",
            "foundation_contact": "info@fordfoundation.org",
            "foundation_city": "New York, NY",
            "prompt_variation": 4
        }
        
        response = requests.get(
            f"{API_BASE_URL}/find-foundation-url/Ford Foundation",
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ GET request successful")
            print(f"📝 Prompt Variation: {result.get('prompt_variation', 'N/A')}")
            print(f"📁 Foundation Data Used: {result.get('foundation_data_used', 'N/A')}")
        else:
            print(f"❌ Status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_api_info():
    """Test the root endpoint for API information."""
    print(f"\n📋 Testing API Information")
    print("-" * 40)
    
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API Version: {result.get('version')}")
            print(f"📊 Foundation Data Integration: {result.get('features', {}).get('foundation_data_integration')}")
            print(f"📝 Supported Prompt Variations: {result.get('features', {}).get('prompt_variations')}")
            print(f"📁 Supported Data Fields: {result.get('features', {}).get('supported_data_fields')}")
        else:
            print(f"❌ Status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting API Tests")
    print("Make sure the API server is running: python main.py")
    print("=" * 60)
    
    test_api_info()
    test_api_with_foundation_data()
    test_get_endpoint()
    
    print(f"\n✅ API Tests Completed!")
    print("💡 You can also test interactively at: http://localhost:8000/docs")
