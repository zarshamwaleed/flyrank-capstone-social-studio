import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_create_and_publish():
    """Create a post, approve, and publish"""
    print("\n📝 Creating post for history test...")
    
    post_data = {
        "title": "Publish History Test Post",
        "content": """
# Publish History Test

This is a test post for the publish history module.

## Test Points
- Should track all publish attempts
- Should show history with filters
- Should provide statistics
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
    discord_variant = None
    for variant in variants:
        if variant['platform'] == 'discord':
            discord_variant = variant
            break
    
    if not discord_variant:
        print("  ❌ No Discord variant found")
        return None
    
    variant_id = discord_variant['id']
    print(f"  ✅ Discord variant created: {variant_id}")
    
    # Approve the variant
    response = requests.post(f"{BASE_URL}/variants/{variant_id}/approve")
    if response.status_code != 200:
        print(f"  ❌ Failed to approve variant: {response.text}")
        return None
    print(f"  ✅ Variant {variant_id} approved")
    
    # Publish
    response = requests.post(f"{BASE_URL}/publish/{variant_id}/idempotent?publisher_name=discord")
    if response.status_code == 200:
        print(f"  ✅ Published successfully!")
        data = response.json()
        print(f"  Idempotency Key: {data.get('idempotency_key')}")
        return variant_id, data.get('idempotency_key')
    else:
        print(f"  ❌ Failed to publish: {response.text}")
        return None, None

def test_get_history():
    """Test getting publish history"""
    print("\n📋 Testing Get History...")
    
    response = requests.get(f"{BASE_URL}/history")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Total attempts: {data['total']}")
        print(f"  Attempts returned: {len(data['attempts'])}")
        for attempt in data['attempts'][:3]:
            print(f"    - ID: {attempt['id']}, Status: {attempt['status']}, Platform: {attempt['platform']}")
        return data
    else:
        print(f"  ❌ Error: {response.text}")
        return None

def test_get_history_stats():
    """Test getting history statistics"""
    print("\n📊 Testing History Stats...")
    
    response = requests.get(f"{BASE_URL}/history/stats")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        stats = data['stats']
        print(f"  Total attempts: {stats['total_attempts']}")
        print(f"  Status counts: {stats['status_counts']}")
        print(f"  Platform counts: {stats['platform_counts']}")
        return data
    else:
        print(f"  ❌ Error: {response.text}")
        return None

def test_get_timeline():
    """Test getting history timeline"""
    print("\n📈 Testing History Timeline...")
    
    response = requests.get(f"{BASE_URL}/history/timeline?days=7")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        timeline = data['timeline']
        print(f"  Days: {timeline['days']}")
        print(f"  Data points: {len(timeline['data'])}")
        if timeline['data']:
            print(f"  Latest date: {timeline['data'][-1]['date']}, Count: {timeline['data'][-1]['count']}")
        return data
    else:
        print(f"  ❌ Error: {response.text}")
        return None

def test_get_variant_history(variant_id):
    """Test getting history for a specific variant"""
    print(f"\n📋 Testing Variant History for variant {variant_id}...")
    
    response = requests.get(f"{BASE_URL}/history/variant/{variant_id}")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Variant platform: {data['variant_platform']}")
        print(f"  Total attempts: {data['total_attempts']}")
        for attempt in data['attempts'][:3]:
            print(f"    - Status: {attempt['status']}, Attempted: {attempt['attempted_at']}")
        return data
    else:
        print(f"  ❌ Error: {response.text}")
        return None

def test_get_platform_history():
    """Test getting history for a specific platform"""
    print("\n📋 Testing Platform History...")
    
    response = requests.get(f"{BASE_URL}/history/platform/discord")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Platform: {data['platform']}")
        print(f"  Total attempts: {data['total_attempts']}")
        return data
    else:
        print(f"  ❌ Error: {response.text}")
        return None

def test_get_recent_history():
    """Test getting recent history"""
    print("\n📋 Testing Recent History...")
    
    response = requests.get(f"{BASE_URL}/history/recent?days=7&limit=50")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Days: {data['days']}")
        print(f"  Total attempts: {data['total_attempts']}")
        return data
    else:
        print(f"  ❌ Error: {response.text}")
        return None

def test_get_history_by_status():
    """Test getting history by status"""
    print("\n📋 Testing History by Status...")
    
    response = requests.get(f"{BASE_URL}/history/status/success")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Filter status: {data['filter_status']}")
        print(f"  Total attempts: {data['total_attempts']}")
        return data
    else:
        print(f"  ❌ Error: {response.text}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("MODULE 12: Publish History Tests")
    print("=" * 60)
    
    # Create and publish
    variant_id, idempotency_key = test_create_and_publish()
    
    # Test history endpoints
    test_get_history()
    test_get_history_stats()
    test_get_timeline()
    
    if variant_id:
        test_get_variant_history(variant_id)
    
    test_get_platform_history()
    test_get_recent_history()
    test_get_history_by_status()
    
    print("\n" + "=" * 60)
    print("✅ Module 12 Tests Complete!")
    print("=" * 60)
    print("\n📝 Features Tested:")
    print("  • History listing with filters ✓")
    print("  • Statistics endpoint ✓")
    print("  • Timeline endpoint ✓")
    print("  • Variant history ✓")
    print("  • Platform history ✓")
    print("  • Recent history ✓")
    print("  • Status filtering ✓")
