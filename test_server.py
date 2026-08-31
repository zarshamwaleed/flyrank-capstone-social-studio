import requests
import json

# Test root endpoint
try:
    response = requests.get("http://localhost:8000/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("✓ Root endpoint working")
except Exception as e:
    print(f"✗ Error: {e}")

# Test health endpoint
try:
    response = requests.get("http://localhost:8000/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("✓ Health endpoint working")
except Exception as e:
    print(f"✗ Error: {e}")
