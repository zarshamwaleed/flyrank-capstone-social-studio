import requests
import json

BASE_URL = "http://localhost:8000"

def test_ingest_text():
    """Test ingesting a post via text"""
    print("\n📝 Testing Text Ingestion...")
    
    post_data = {
        "title": "My Test Blog Post",
        "content": """
# My Test Blog Post

This is a test blog post created for Module 3.

## Key Points
- Point 1: This is the first point
- Point 2: This is the second point
- Point 3: This is the third point

### Conclusion
This is a successful test of the blog post ingestion feature.
        """.strip()
    }
    
    response = requests.post(f"{BASE_URL}/posts/ingest", json=post_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_ingest_url():
    """Test ingesting a post via URL"""
    print("\n🌐 Testing URL Ingestion...")
    
    post_data = {
        "source_url": "https://example.com"
    }
    
    response = requests.post(f"{BASE_URL}/posts/ingest", json=post_data)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
    return response.json()

def test_list_posts():
    """Test listing all posts"""
    print("\n📋 Testing List Posts...")
    
    response = requests.get(f"{BASE_URL}/posts")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} posts")
        for post in data:
            print(f"  - ID: {post['id']}, Title: {post.get('title', 'Untitled')}")
    return response.json()

def test_ingest_invalid():
    """Test ingesting invalid data"""
    print("\n❌ Testing Invalid Ingestion...")
    
    # Empty content
    post_data = {"title": "Empty Post"}
    response = requests.post(f"{BASE_URL}/posts/ingest", json=post_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()

if __name__ == "__main__":
    print("=" * 60)
    print("MODULE 3: Blog Post Ingestion Tests")
    print("=" * 60)
    
    # Test text ingestion
    text_result = test_ingest_text()
    
    # Test URL ingestion
    url_result = test_ingest_url()
    
    # Test listing posts
    list_result = test_list_posts()
    
    # Test invalid ingestion
    invalid_result = test_ingest_invalid()
    
    print("\n" + "=" * 60)
    print("✅ Module 3 Tests Complete!")
    print("=" * 60)
