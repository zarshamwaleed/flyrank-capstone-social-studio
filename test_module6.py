import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_create_post_and_variants():
    """Create a post and generate variants"""
    print("\n📝 Creating test post...")
    
    post_data = {
        "title": "Review Workflow Test",
        "content": """
# Review Workflow Test Post

This is a test post for the review workflow module.

## Key Points
- Variants must be approved before scheduling
- Rejected variants can be edited and resubmitted
- Only approved variants can be scheduled
        """.strip()
    }
    
    response = requests.post(f"{BASE_URL}/posts/ingest", json=post_data)
    if response.status_code == 200:
        data = response.json()
        post_id = data['post']['id']
        print(f"✅ Post created with ID: {post_id}")
        
        # Generate variants
        print(f"\n🔄 Generating variants for post {post_id}...")
        response = requests.post(f"{BASE_URL}/posts/{post_id}/variants/generate")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Generated {len(data['variants'])} variants")
            return post_id, data['variants']
    
    return None, None

def test_approve_variant(variant_id):
    """Test approving a variant"""
    print(f"\n✅ Testing Approve Variant {variant_id}...")
    
    response = requests.post(f"{BASE_URL}/variants/{variant_id}/approve")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Variant approved: {data['message']}")
        print(f"  Status: {data['variant']['status']}")
        return True
    else:
        print(f"  ❌ Failed: {response.text}")
        return False

def test_reject_variant(variant_id):
    """Test rejecting a variant"""
    print(f"\n❌ Testing Reject Variant {variant_id}...")
    
    response = requests.post(f"{BASE_URL}/variants/{variant_id}/reject?reason=Does not meet quality standards")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Variant rejected: {data['message']}")
        print(f"  Status: {data['variant']['status']}")
        return True
    else:
        print(f"  ❌ Failed: {response.text}")
        return False

def test_edit_variant(variant_id):
    """Test editing a variant"""
    print(f"\n✏️ Testing Edit Variant {variant_id}...")
    
    new_content = "This is the edited content for this variant. It should pass validation."
    response = requests.patch(
        f"{BASE_URL}/variants/{variant_id}/edit",
        params={"content": new_content}
    )
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Variant edited: {data['message']}")
        return True
    else:
        print(f"  ❌ Failed: {response.text}")
        return False

def test_schedule_variant(variant_id):
    """Test scheduling a variant"""
    print(f"\n📅 Testing Schedule Variant {variant_id}...")
    
    # Schedule 1 hour from now
    schedule_time = (datetime.now() + timedelta(hours=1)).isoformat()
    response = requests.post(
        f"{BASE_URL}/variants/{variant_id}/schedule",
        params={"scheduled_time": schedule_time}
    )
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Variant scheduled: {data['message']}")
        print(f"  Scheduled for: {data['variant']['scheduled_for']}")
        return True
    else:
        print(f"  ❌ Failed: {response.text}")
        return False

def test_schedule_unapproved_variant(variant_id):
    """Test scheduling an unapproved variant (should fail)"""
    print(f"\n🚫 Testing Schedule Unapproved Variant {variant_id}...")
    
    schedule_time = (datetime.now() + timedelta(hours=1)).isoformat()
    response = requests.post(
        f"{BASE_URL}/variants/{variant_id}/schedule",
        params={"scheduled_time": schedule_time}
    )
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 403:
        print(f"  ✅ Correctly blocked: {response.json()['detail']}")
        return True
    else:
        print(f"  ❌ Should have returned 403, got {response.status_code}")
        return False

def test_review_stats():
    """Test getting review statistics"""
    print(f"\n📊 Testing Review Stats...")
    
    response = requests.get(f"{BASE_URL}/variants/review/stats")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        stats = data['stats']
        print(f"  Total variants: {stats['total']}")
        print(f"  Draft: {stats.get('draft', 0)}")
        print(f"  Approved: {stats.get('approved', 0)}")
        print(f"  Rejected: {stats.get('rejected', 0)}")
        return True
    else:
        print(f"  ❌ Failed: {response.text}")
        return False

def test_can_schedule(variant_id):
    """Test checking if a variant can be scheduled"""
    print(f"\n🔍 Testing Can Schedule Variant {variant_id}...")
    
    response = requests.get(f"{BASE_URL}/variants/{variant_id}/can-schedule")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Can schedule: {data['can_schedule']}")
        print(f"  Message: {data['message']}")
        return True
    else:
        print(f"  ❌ Failed: {response.text}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("MODULE 6: Review Workflow Tests")
    print("=" * 60)
    
    # Create a post and variants
    post_id, variants = test_create_post_and_variants()
    
    if post_id and variants:
        # Get variant IDs
        variant_ids = [v['id'] for v in variants]
        print(f"\n📋 Variant IDs: {variant_ids}")
        
        # Test workflow
        print("\n" + "=" * 40)
        print("Testing Review Workflow")
        print("=" * 40)
        
        # 1. Try to schedule unapproved variant (should fail)
        test_schedule_unapproved_variant(variant_ids[0])
        
        # 2. Check if variant can be scheduled (should be false)
        test_can_schedule(variant_ids[0])
        
        # 3. Approve a variant
        test_approve_variant(variant_ids[0])
        
        # 4. Check if variant can be scheduled (should be true)
        test_can_schedule(variant_ids[0])
        
        # 5. Schedule the approved variant
        test_schedule_variant(variant_ids[0])
        
        # 6. Reject another variant
        if len(variant_ids) > 1:
            test_reject_variant(variant_ids[1])
        
        # 7. Edit a rejected variant
        if len(variant_ids) > 1:
            test_edit_variant(variant_ids[1])
            
            # Re-approve after editing
            test_approve_variant(variant_ids[1])
        
        # 8. Get review stats
        test_review_stats()
    
    print("\n" + "=" * 60)
    print("✅ Module 6 Tests Complete!")
    print("=" * 60)
