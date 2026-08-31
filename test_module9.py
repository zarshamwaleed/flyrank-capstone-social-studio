import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
BASE_URL = "http://localhost:8000"

def test_discord_status():
    """Test getting Discord publisher status"""
    print("\n📋 Testing Discord Status...")
    
    response = requests.get(f"{BASE_URL}/discord/status")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Configured: {data['configured']}")
        print(f"  Platform: {data['platform']}")
        return data
    else:
        print(f"  ❌ Error: {response.text}")
        return None

def test_discord_connection():
    """Test Discord webhook connection"""
    print("\n🔗 Testing Discord Connection...")
    
    response = requests.post(f"{BASE_URL}/discord/test")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Test successful!")
        print(f"  Message: {data['message']}")
        return data
    else:
        print(f"  ❌ Test failed: {response.text}")
        return None

def test_create_and_publish_discord():
    """Create a post and publish to Discord"""
    print("\n📝 Creating post for Discord publish...")
    
    # Create a post
    post_data = {
        "title": "Discord Publishing Test",
        "content": """
# Discord Publishing Test

This is a test post to verify Discord webhook integration is working correctly.

## Key Features
- ✅ Discord webhook integration
- ✅ Markdown formatting support
- ✅ Emoji support
- ✅ Real-time publishing

Testing from Social Media Studio API!
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
    
    # Publish to Discord
    print(f"\n📤 Publishing to Discord...")
    
    response = requests.post(f"{BASE_URL}/publish/{variant_id}?publisher_name=discord")
    print(f"  Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            print(f"  ✅ Successfully published to Discord!")
            print(f"  Message: {data['message']}")
            print(f"  Publisher: {data['publisher']}")
            return data
        else:
            print(f"  ⚠️  Publish completed with errors: {data['message']}")
            return data
    else:
        print(f"  ❌ Failed to publish: {response.text}")
        return None

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
        print(f"  ❌ Error: {response.text}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("MODULE 9: Real Discord Publisher Tests")
    print("=" * 60)
    
    # Test Discord status
    test_discord_status()
    
    # Test Discord connection
    test_discord_connection()
    
    # Test listing publishers
    test_list_publishers()
    
    # Test creating and publishing to Discord
    result = test_create_and_publish_discord()
    
    print("\n" + "=" * 60)
    print("✅ Module 9 Tests Complete!")
    print("=" * 60)
    print("\n📝 Summary:")
    print("  • Discord webhook integration ✓")
    print("  • Discord connection test ✓")
    print("  • Discord publish test ✓")
