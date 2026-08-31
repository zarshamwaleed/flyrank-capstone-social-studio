import requests
import json

BASE_URL = "http://localhost:8000"

def test_list_publishers():
    """Test listing all publishers"""
    print("\n📋 Testing List Publishers...")
    
    response = requests.get(f"{BASE_URL}/publishers")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Publishers: {data['publishers']}")
        print(f"  Statuses: {data['statuses']}")
        return data
    else:
        print(f"  ❌ Failed: {response.text}")
        return None

def test_publish_with_mock_x():
    """Test publishing with Mock X"""
    print("\n🐦 Testing Mock X Publisher...")
    
    # First create a new post and variants
    post_data = {
        "title": "Mock X Test Post",
        "content": "# Mock X Test Post\n\nThis is a test for the Mock X publisher."
    }
    response = requests.post(f"{BASE_URL}/posts/ingest", json=post_data)
    if response.status_code != 200:
        print(f"  ❌ Failed to create post: {response.text}")
        return None
    
    post_id = response.json()['post']['id']
    print(f"  Post created: {post_id}")
    
    # Generate variants
    response = requests.post(f"{BASE_URL}/posts/{post_id}/variants/generate")
    if response.status_code != 200:
        print(f"  ❌ Failed to generate variants: {response.text}")
        return None
    
    variants = response.json()['variants']
    variant_id = variants[0]['id']
    print(f"  Variant created: {variant_id}")
    
    # Approve the variant
    response = requests.post(f"{BASE_URL}/variants/{variant_id}/approve")
    if response.status_code != 200:
        print(f"  ❌ Failed to approve variant: {response.text}")
        return None
    print(f"  Variant {variant_id} approved")
    
    # Publish with Mock X
    response = requests.post(f"{BASE_URL}/publish/{variant_id}?publisher_name=mock_x")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Mock X publish successful!")
        print(f"  Status: {data['status']}")
        print(f"  Message: {data['message']}")
        print(f"  Publisher: {data['publisher']}")
        return data
    else:
        print(f"  ❌ Failed: {response.text}")
        return None

def test_publish_with_mock_linkedin():
    """Test publishing with Mock LinkedIn"""
    print("\n💼 Testing Mock LinkedIn Publisher...")
    
    # Create another post
    post_data = {
        "title": "Mock LinkedIn Test Post",
        "content": "# Mock LinkedIn Test Post\n\nThis is a test for the Mock LinkedIn publisher."
    }
    response = requests.post(f"{BASE_URL}/posts/ingest", json=post_data)
    if response.status_code != 200:
        print(f"  ❌ Failed to create post: {response.text}")
        return None
    
    post_id = response.json()['post']['id']
    print(f"  Post created: {post_id}")
    
    # Generate variants
    response = requests.post(f"{BASE_URL}/posts/{post_id}/variants/generate")
    if response.status_code != 200:
        print(f"  ❌ Failed to generate variants: {response.text}")
        return None
    
    variants = response.json()['variants']
    variant_id = variants[0]['id']
    print(f"  Variant created: {variant_id}")
    
    # Approve the variant
    response = requests.post(f"{BASE_URL}/variants/{variant_id}/approve")
    if response.status_code != 200:
        print(f"  ❌ Failed to approve variant: {response.text}")
        return None
    print(f"  Variant {variant_id} approved")
    
    # Publish with Mock LinkedIn
    response = requests.post(f"{BASE_URL}/publish/{variant_id}?publisher_name=mock_linkedin")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Mock LinkedIn publish successful!")
        print(f"  Status: {data['status']}")
        print(f"  Message: {data['message']}")
        print(f"  Publisher: {data['publisher']}")
        return data
    else:
        print(f"  ❌ Failed: {response.text}")
        return None

def test_publish_mock_discord():
    """Test publishing with Mock Discord"""
    print("\n💬 Testing Mock Discord Publisher...")
    
    # Create another post
    post_data = {
        "title": "Mock Discord Test Post",
        "content": "# Mock Discord Test Post\n\nThis is a test for the Mock Discord publisher."
    }
    response = requests.post(f"{BASE_URL}/posts/ingest", json=post_data)
    if response.status_code != 200:
        print(f"  ❌ Failed to create post: {response.text}")
        return None
    
    post_id = response.json()['post']['id']
    print(f"  Post created: {post_id}")
    
    # Generate variants
    response = requests.post(f"{BASE_URL}/posts/{post_id}/variants/generate")
    if response.status_code != 200:
        print(f"  ❌ Failed to generate variants: {response.text}")
        return None
    
    variants = response.json()['variants']
    variant_id = variants[0]['id']
    print(f"  Variant created: {variant_id}")
    
    # Approve the variant
    response = requests.post(f"{BASE_URL}/variants/{variant_id}/approve")
    if response.status_code != 200:
        print(f"  ❌ Failed to approve variant: {response.text}")
        return None
    print(f"  Variant {variant_id} approved")
    
    # Publish with Mock Discord
    response = requests.post(f"{BASE_URL}/publish/{variant_id}?publisher_name=mock_discord")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Mock Discord publish successful!")
        print(f"  Status: {data['status']}")
        print(f"  Message: {data['message']}")
        print(f"  Publisher: {data['publisher']}")
        return data
    else:
        print(f"  ❌ Failed: {response.text}")
        return None

def test_preview_mock_publish():
    """Test previewing a mock publish"""
    print("\n👁️ Testing Mock Publish Preview...")
    
    # Use variant 4 (which exists)
    response = requests.post(f"{BASE_URL}/publish/mock/preview?variant_id=4&publisher_name=mock_x")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Preview successful!")
        print(f"  Message: {data['message']}")
        if 'preview' in data:
            preview = data['preview']
            print(f"  Characters: {preview['characters']}")
            print(f"  Content preview: {preview['content'][:50]}...")
        return data
    else:
        print(f"  ❌ Failed: {response.text}")
        return None

def test_publisher_factory():
    """Test publisher factory functionality"""
    print("\n🏭 Testing Publisher Factory...")
    
    response = requests.get(f"{BASE_URL}/publishers")
    if response.status_code == 200:
        data = response.json()
        print(f"  Available publishers: {data['publishers']}")
        print(f"  Total: {len(data['publishers'])} publishers")
        return True
    else:
        print(f"  ❌ Failed: {response.text}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("MODULE 7: Publisher Adapter Architecture Tests")
    print("=" * 60)
    
    # Test listing publishers
    test_list_publishers()
    
    # Test publishing with different publishers
    test_publish_with_mock_x()
    test_publish_with_mock_linkedin()
    test_publish_mock_discord()
    
    # Test preview
    test_preview_mock_publish()
    
    # Test publisher factory
    test_publisher_factory()
    
    print("\n" + "=" * 60)
    print("✅ Module 7 Tests Complete!")
    print("=" * 60)
    print("\n📝 Note: To test the real Discord publisher:")
    print("  1. Set DISCORD_WEBHOOK_URL in .env")
    print("  2. Configure with: POST /publishers/discord/configure")
    print("  3. Publish with: POST /publish/4?publisher_name=discord")
