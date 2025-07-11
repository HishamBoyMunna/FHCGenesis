import requests
import json

# Test the API endpoints
base_url = "http://127.0.0.1:5000"

def test_api():
    print("Testing API endpoints...")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Server is running (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Server is not running: {e}")
        return
    
    # Test 2: Try to access devices without authentication (should fail)
    try:
        response = requests.get(f"{base_url}/api/devices")
        if response.status_code == 401:
            print("✅ API correctly requires authentication")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing devices API: {e}")

if __name__ == "__main__":
    test_api() 