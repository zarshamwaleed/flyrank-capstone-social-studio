import requests
import json

BASE_URL = "http://localhost:8000"

def test_create_post():
    """Create a test post"""
    print("\n📝 Creating test post...")
    
    post_data = {
        "title": "The Future of AI in Social Media Marketing",
        "content": """
# The Future of AI in Social Media Marketing

Artificial Intelligence is revolutionizing how businesses approach social media marketing.

## Key Trends
- AI-powered content creation tools are becoming mainstream
- Predictive analytics help optimize posting schedules
- Natural Language Processing enables better audience engagement
- Automated customer service through chatbots
- Personalized content delivery at scale

## Market Impact
The global AI in social media market is projected to grow from .2 billion to .8 billion by 2028, representing a CAGR of 37.2%.

## Conclusion
AI is not just a trend; it's becoming a fundamental tool for social media success. Companies that embrace AI-driven strategies will have a significant competitive advantage.
        """.strip()
    }
    
    response = requests.post(f"{BASE_URL}/posts/ingest", json=post_data)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Post created with ID: {data['post']['id']}")
        return data['post']['id']
    else:
        print(f"❌ Failed to create post: {response.text}")
        return None

def test_generate_variants(post_id):
    """Generate variants for a post"""
    print(f"\n🔄 Generating variants for post {post_id}...")
    
    response = requests.post(f"{BASE_URL}/posts/{post_id}/variants/generate")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Generated variants for platforms: {data['platforms_generated']}")
        print(f"   Total variants: {len(data['variants'])}")
        
        for variant in data['variants']:
            print(f"\n   📱 Platform: {variant['platform']}")
            print(f"      Status: {variant['status']}")
            print(f"      Content preview: {variant['content'][:100]}...")
            if variant.get('hashtags'):
                print(f"      Hashtags: {variant['hashtags']}")
        
        return data['variants']
    else:
        print(f"❌ Failed to generate variants: {response.text}")
        return None

def test_get_variants(post_id):
    """Get all variants for a post"""
    print(f"\n📋 Getting variants for post {post_id}...")
    
    response = requests.get(f"{BASE_URL}/posts/{post_id}/variants")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data)} variants")
        for variant in data:
            print(f"   - {variant['platform']}: {variant['status']} (ID: {variant['id']})")
        return data
    else:
        print(f"❌ Failed to get variants: {response.text}")
        return None

def test_update_variant_status(variant_id):
    """Update a variant's status"""
    print(f"\n🔄 Updating variant {variant_id} status to 'approved'...")
    
    response = requests.patch(f"{BASE_URL}/variants/{variant_id}/status?status=approved")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Variant status updated: {data['message']}")
        return data
    else:
        print(f"❌ Failed to update status: {response.text}")
        return None

def test_get_platform_constraints():
    """Get platform constraints"""
    print("\n📋 Getting platform constraints...")
    
    response = requests.get(f"{BASE_URL}/platforms/constraints")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Platform constraints:")
        for platform, constraints in data['constraints'].items():
            print(f"   - {platform}: max_length={constraints['max_length']}, tone={constraints['tone']}")
        return data
    else:
        print(f"❌ Failed to get constraints: {response.text}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("MODULE 4: Variant Generation Tests")
    print("=" * 60)
    
    # Test creating a post
    post_id = test_create_post()
    
    if post_id:
        # Test generating variants
        variants = test_generate_variants(post_id)
        
        # Test getting variants
        test_get_variants(post_id)
        
        # Test updating a variant status
        if variants and len(variants) > 0:
            test_update_variant_status(variants[0]['id'])
        
        # Test getting platform constraints
        test_get_platform_constraints()
    
    print("\n" + "=" * 60)
    print("✅ Module 4 Tests Complete!")
    print("=" * 60)
