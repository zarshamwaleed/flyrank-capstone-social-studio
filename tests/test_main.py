import requests

BASE_URL = "http://localhost:8000"

def test_root_endpoint():
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert response.json() == {"message": "Social Media Studio API is running"}
    print("✅ Root endpoint test passed!")

def test_health_endpoint():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Social Media Studio API"
    print("✅ Health endpoint test passed!")

if __name__ == "__main__":
    test_root_endpoint()
    test_health_endpoint()
    print("✅ All tests passed!")
