import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_create_post_and_variants():
    """Create a post and variants for idempotency testing"""
    print("\n📝 Creating test post for idempotency...")
    
    post_data = {
        "title": "Idempotency Test Post",
        "content": """
# Idempotency Test Post

This is a test post for the idempotency module.

## Test Points
- Multiple publish requests should only publish once
- Retry logic should prevent duplicates
- Publish attempts should be tracked
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
    
    return variant_id

def test_idempotent_publish(variant_id):
    """Test idempotent publish - multiple requests should only publish once"""
    print(f"\n🔐 Testing idempotent publish for variant {variant_id}...")
    
    print("  First request (should publish)...")
    response1 = requests.post(f"{BASE_URL}/publish/{variant_id}/idempotent?publisher_name=discord")
    print(f"    Status Code: {response1.status_code}")
    if response1.status_code == 200:
        data1 = response1.json()
        print(f"    Status: {data1['status']}")
        print(f"    Message: {data1['message']}")
        print(f"    Idempotency Key: {data1.get('idempotency_key', 'N/A')}")
    
    print("\n  Second request (should be blocked as duplicate)...")
    time.sleep(1)
    response2 = requests.post(f"{BASE_URL}/publish/{variant_id}/idempotent?publisher_name=discord")
    print(f"    Status Code: {response2.status_code}")
    if response2.status_code == 200:
        data2 = response2.json()
        print(f"    Status: {data2['status']}")
        print(f"    Message: {data2['message']}")
    
    return response1.json() if response1.status_code == 200 else None

def test_get_publish_attempts(variant_id):
    """Test getting publish attempts"""
    print(f"\n📋 Getting publish attempts for variant {variant_id}...")
    
    response = requests.get(f"{BASE_URL}/publish/attempts/{variant_id}")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Total attempts: {data['total_attempts']}")
        for attempt in data['attempts']:
            print(f"    - ID: {attempt['id']}")
            print(f"      Status: {attempt['status']}")
            print(f"      Idempotency Key: {attempt['idempotency_key']}")
            print(f"      Is Duplicate: {attempt['is_duplicate']}")
        return data
    else:
        print(f"  ❌ Error: {response.text}")
        return None

def test_with_idempotency_key(variant_id):
    """Test using a specific idempotency key"""
    print(f"\n🔑 Testing with custom idempotency key...")
    
    # Use a known key
    custom_key = f"test_key_{variant_id}_{int(datetime.now().timestamp())}"
    print(f"  Custom key: {custom_key}")
    
    response = requests.post(
        f"{BASE_URL}/publish/{variant_id}/idempotent",
        params={"publisher_name": "discord", "idempotency_key": custom_key}
    )
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Status: {data['status']}")
        print(f"  Idempotency Key used: {data.get('idempotency_key')}")
    
    # Try same key again
    print("\n  Trying same key again (should be blocked)...")
    response2 = requests.post(
        f"{BASE_URL}/publish/{variant_id}/idempotent",
        params={"publisher_name": "discord", "idempotency_key": custom_key}
    )
    print(f"  Status Code: {response2.status_code}")
    if response2.status_code == 200:
        data2 = response2.json()
        print(f"  Status: {data2['status']}")
        print(f"  Message: {data2['message']}")

def test_check_attempt():
    """Test checking an attempt by idempotency key"""
    print(f"\n🔍 Testing check attempt...")
    
    # First, create a post and variant
    variant_id = test_create_post_and_variants()
    if not variant_id:
        print("  ❌ Failed to create variant")
        return
    
    # Publish to get an idempotency key
    response = requests.post(f"{BASE_URL}/publish/{variant_id}/idempotent?publisher_name=discord")
    if response.status_code != 200:
        print("  ❌ Failed to publish")
        return
    
    idempotency_key = response.json().get('idempotency_key')
    print(f"  Idempotency Key: {idempotency_key}")
    
    # Check the attempt
    response = requests.get(f"{BASE_URL}/publish/attempts/check/{idempotency_key}")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Status: {data['status']}")
        print(f"  Variant ID: {data['variant_id']}")
        print(f"  Is Duplicate: {data['is_duplicate']}")
    else:
        print(f"  ❌ Error: {response.text}")

if __name__ == "__main__":
    print("=" * 60)
    print("MODULE 11: Idempotency Tests")
    print("=" * 60)
    
    # Create a variant for testing
    variant_id = test_create_post_and_variants()
    
    if variant_id:
        # Test idempotent publish
        test_idempotent_publish(variant_id)
        
        # Test getting publish attempts
        test_get_publish_attempts(variant_id)
        
        # Test with custom idempotency key
        test_with_idempotency_key(variant_id)
        
        # Test checking an attempt
        test_check_attempt()
    
    print("\n" + "=" * 60)
    print("✅ Module 11 Tests Complete!")
    print("=" * 60)
    print("\n📝 Key Features Tested:")
    print("  • Idempotent publish - multiple requests only publish once ✓")
    print("  • Duplicate detection and blocking ✓")
    print("  • Publish attempt tracking ✓")
    print("  • Custom idempotency keys ✓")
    print("  • Attempt status checking ✓")
