import requests
import json

BASE_URL = "http://localhost:8000"

def test_validate_content():
    """Test content validation"""
    print("\n📝 Testing Content Validation...")
    
    # Test valid content
    print("\n  ✅ Testing valid content...")
    test_data = {
        "platform": "twitter",
        "content": "This is a short tweet about AI in marketing. #AI #Marketing",
        "hashtags": "#AI #Marketing"
    }
    response = requests.post(f"{BASE_URL}/validate", json=test_data)
    print(f"    Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    Valid: {data['valid']}")
        print(f"    Errors: {data['errors']}")
        print(f"    Warnings: {data['warnings']}")
    
    # Test invalid content (too long)
    print("\n  ❌ Testing invalid content (too long)...")
    long_content = "A" * 300
    test_data = {
        "platform": "twitter",
        "content": long_content,
        "hashtags": "#AI #Marketing"
    }
    response = requests.post(f"{BASE_URL}/validate", json=test_data)
    print(f"    Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    Valid: {data['valid']}")
        print(f"    Errors: {data['errors']}")
    
    # Test invalid hashtags (too many)
    print("\n  ❌ Testing invalid hashtags (too many)...")
    test_data = {
        "platform": "twitter",
        "content": "This is a tweet with too many hashtags",
        "hashtags": "#AI #Marketing #Tech #Innovation #Future"
    }
    response = requests.post(f"{BASE_URL}/validate", json=test_data)
    print(f"    Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    Valid: {data['valid']}")
        print(f"    Errors: {data['errors']}")

def test_validate_existing_variant():
    """Test validating an existing variant"""
    print("\n📋 Testing Existing Variant Validation...")
    
    response = requests.get(f"{BASE_URL}/validate/variant/1")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Variant ID: {data['variant_id']}")
        print(f"  Platform: {data['platform']}")
        print(f"  Valid: {data['valid']}")
        if data['errors']:
            print(f"  Errors: {data['errors']}")

def test_validate_post_variants():
    """Test validating all variants for a post"""
    print("\n📊 Testing Post Variants Validation...")
    
    response = requests.get(f"{BASE_URL}/validate/post/4")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Post ID: {data['post_id']}")
        print(f"  All Valid: {data['all_valid']}")
        print(f"  Results:")
        for platform, result in data['results'].items():
            print(f"    - {platform}: {result['valid']}")

def test_constraints_summary():
    """Test getting constraints summary"""
    print("\n📋 Testing Constraints Summary...")
    
    response = requests.get(f"{BASE_URL}/constraints/summary")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Constraints:")
        for platform, constraints in data['constraints'].items():
            print(f"    - {platform}: max_length={constraints['max_length']}, tone={constraints['tone']}")

if __name__ == "__main__":
    print("=" * 60)
    print("MODULE 5: Constraint Validation Tests")
    print("=" * 60)
    
    test_validate_content()
    test_validate_existing_variant()
    test_validate_post_variants()
    test_constraints_summary()
    
    print("\n" + "=" * 60)
    print("✅ Module 5 Tests Complete!")
    print("=" * 60)
