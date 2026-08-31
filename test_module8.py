import requests
import json

BASE_URL = "http://localhost:8000"

def test_create_and_publish():
    """Create a post, generate variants, approve, and publish"""
    print("\n📝 Creating test post for Module 8...")
    
    post_data = {
        "title": "Module 8 Test Post",
        "content": """
# Module 8 Test Post

This is a test post for Module 8 - Mock Publishers Testing.

## Key Points
- Mock publishers should record all published posts
- History should be viewable
- History should be clearable
- Statistics should be available
        """.strip()
    }
    
    response = requests.post(f"{BASE_URL}/posts/ingest", json=post_data)
    if response.status_code != 200:
        print(f"  ❌ Failed to create post: {response.text}")
        return None
    
    post_id = response.json()['post']['id']
    print(f"  ✅ Post created: {post_id}")
    
    # Generate variants
    response = requests.post(f"{BASE_URL}/posts/{post_id}/variants/generate")
    if response.status_code != 200:
        print(f"  ❌ Failed to generate variants: {response.text}")
        return None
    
    variants = response.json()['variants']
    print(f"  ✅ Generated {len(variants)} variants")
    
    # Approve and publish each variant with different publishers
    results = []
    publishers = ["mock_x", "mock_linkedin", "mock_discord"]
    
    for i, variant in enumerate(variants):
        variant_id = variant['id']
        publisher = publishers[i % len(publishers)]
        
        # Approve
        response = requests.post(f"{BASE_URL}/variants/{variant_id}/approve")
        if response.status_code != 200:
            print(f"  ❌ Failed to approve variant {variant_id}")
            continue
        
        # Publish
        response = requests.post(f"{BASE_URL}/publish/{variant_id}?publisher_name={publisher}")
        if response.status_code == 200:
            print(f"  ✅ Published variant {variant_id} to {publisher}")
            results.append({"variant_id": variant_id, "publisher": publisher})
        else:
            print(f"  ❌ Failed to publish variant {variant_id} to {publisher}: {response.text}")
    
    return results

def test_get_mock_history():
    """Test getting history for mock publishers"""
    print("\n📋 Testing Mock Publisher History...")
    
    publishers = ["mock_x", "mock_linkedin", "mock_discord"]
    
    for publisher in publishers:
        response = requests.get(f"{BASE_URL}/mock/publishers/{publisher}/history")
        print(f"  {publisher}: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"    Total posts: {data['total_posts']}")
            if data['total_posts'] > 0:
                last = data['history'][-1]
                print(f"    Last post: {last['id']} - {last['characters']} chars")
        else:
            print(f"    ❌ Error: {response.text}")

def test_get_mock_stats():
    """Test getting statistics for mock publishers"""
    print("\n📊 Testing Mock Publisher Statistics...")
    
    publishers = ["mock_x", "mock_linkedin", "mock_discord"]
    
    for publisher in publishers:
        response = requests.get(f"{BASE_URL}/mock/publishers/{publisher}/stats")
        print(f"  {publisher}: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            stats = data['stats']
            print(f"    Configured: {stats['configured']}")
            print(f"    Total posts: {stats.get('total_posts', 0)}")
            if stats.get('last_post'):
                print(f"    Last post: {stats['last_post']['id']}")
        else:
            print(f"    ❌ Error: {response.text}")

def test_get_all_mock_history():
    """Test getting history for all mock publishers"""
    print("\n📋 Testing All Mock Publishers History...")
    
    response = requests.get(f"{BASE_URL}/mock/publishers/all/history")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Total posts across all publishers: {data['total_posts']}")
        for publisher, info in data['publishers'].items():
            print(f"    {publisher}: {info['total_posts']} posts")
    else:
        print(f"  ❌ Error: {response.text}")

def test_clear_mock_history():
    """Test clearing history for a mock publisher"""
    print("\n🗑️ Testing Clear Mock Publisher History...")
    
    # First, check current count
    response = requests.get(f"{BASE_URL}/mock/publishers/mock_x/history")
    if response.status_code == 200:
        before_count = response.json()['total_posts']
        print(f"  Before clearing: {before_count} posts")
    
    # Clear history
    response = requests.delete(f"{BASE_URL}/mock/publishers/mock_x/history")
    print(f"  Clear: Status {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Cleared {data['cleared_count']} posts")
    
    # Verify cleared
    response = requests.get(f"{BASE_URL}/mock/publishers/mock_x/history")
    if response.status_code == 200:
        after_count = response.json()['total_posts']
        print(f"  After clearing: {after_count} posts")
        if after_count == 0:
            print("  ✅ History cleared successfully!")
        else:
            print(f"  ⚠️ Expected 0 posts, got {after_count}")

if __name__ == "__main__":
    print("=" * 60)
    print("MODULE 8: Mock Publishers Testing")
    print("=" * 60)
    
    # Test creating and publishing
    results = test_create_and_publish()
    
    # Test getting history
    test_get_mock_history()
    
    # Test getting stats
    test_get_mock_stats()
    
    # Test getting all history
    test_get_all_mock_history()
    
    # Test clearing history
    test_clear_mock_history()
    
    print("\n" + "=" * 60)
    print("✅ Module 8 Tests Complete!")
    print("=" * 60)
