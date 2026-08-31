import urllib.request
import json
import sys

def test_server():
    print("Testing Social Media Studio API...")
    print("=" * 50)
    
    try:
        # Test root
        req = urllib.request.Request("http://localhost:8000/")
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())
            print(f"Root endpoint: {data}")
            if data.get("message") == "Social Media Studio API is running":
                print("✅ Root endpoint: PASS")
            else:
                print(f"❌ Root endpoint: FAIL - Got: {data}")
                return False
                
        # Test health
        req = urllib.request.Request("http://localhost:8000/health")
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())
            print(f"Health endpoint: {data}")
            if data.get("status") == "healthy":
                print("✅ Health endpoint: PASS")
            else:
                print(f"❌ Health endpoint: FAIL - Got: {data}")
                return False
                
        print("\n🎉 All tests passed!")
        return True
        
    except urllib.error.URLError as e:
        print(f"❌ Connection error: {e}")
        print("   Make sure the server is running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1)
