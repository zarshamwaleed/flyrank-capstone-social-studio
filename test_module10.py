import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_scheduler_status():
    """Test getting scheduler status"""
    print("\n📋 Testing Scheduler Status...")
    
    response = requests.get(f"{BASE_URL}/scheduler/status")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Scheduler running: {data['scheduler']['running']}")
        print(f"  Jobs: {data['scheduler']['jobs']}")
        return data
    else:
        print(f"  ❌ Error: {response.text}")
        return None

def test_create_post_and_variants():
    """Create a post and variants for scheduling"""
    print("\n📝 Creating post for scheduling...")
    
    post_data = {
        "title": "Scheduled Publishing Test",
        "content": """
# Scheduled Publishing Test

This is a test post for the scheduling module.

## Test Points
- Variant should be approved
- Scheduled time should be set
- Scheduler should publish at the right time
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
    
    # Set scheduled time (1 minute from now)
    schedule_time = (datetime.now() + timedelta(minutes=1)).isoformat()
    response = requests.post(
        f"{BASE_URL}/variants/{variant_id}/schedule",
        params={"scheduled_time": schedule_time}
    )
    if response.status_code != 200:
        print(f"  ❌ Failed to schedule variant: {response.text}")
        return None
    print(f"  ✅ Variant {variant_id} scheduled for {schedule_time}")
    
    return variant_id

def test_schedule_publish(variant_id):
    """Test scheduling a publish job"""
    print(f"\n📅 Scheduling publish for variant {variant_id}...")
    
    response = requests.post(f"{BASE_URL}/scheduler/schedule/{variant_id}?publisher=discord")
    print(f"  Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Job scheduled!")
        print(f"  Job ID: {data['job_id']}")
        print(f"  Scheduled for: {data['scheduled_for']}")
        print(f"  Publisher: {data['publisher']}")
        return data
    else:
        print(f"  ❌ Failed: {response.text}")
        return None

def test_list_jobs():
    """Test listing scheduled jobs"""
    print("\n📋 Listing scheduled jobs...")
    
    response = requests.get(f"{BASE_URL}/scheduler/jobs")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Total jobs: {data['total']}")
        for job in data['jobs']:
            print(f"    - {job['id']}: {job['name']}")
            print(f"      Next run: {job['next_run_time']}")
        return data
    else:
        print(f"  ❌ Error: {response.text}")
        return None

def test_get_due_variants():
    """Test getting due variants"""
    print("\n📋 Getting due variants...")
    
    response = requests.get(f"{BASE_URL}/scheduler/due")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Due variants: {data['due_count']}")
        return data
    else:
        print(f"  ❌ Error: {response.text}")
        return None

def test_get_scheduled_variants():
    """Test getting scheduled variants"""
    print("\n📋 Getting scheduled variants...")
    
    response = requests.get(f"{BASE_URL}/scheduler/scheduled")
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Scheduled variants: {data['scheduled_count']}")
        return data
    else:
        print(f"  ❌ Error: {response.text}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("MODULE 10: Scheduling Tests")
    print("=" * 60)
    
    # Test scheduler status
    test_scheduler_status()
    
    # Create a post and variants
    variant_id = test_create_post_and_variants()
    
    if variant_id:
        # Schedule the publish
        test_schedule_publish(variant_id)
        
        # List jobs
        test_list_jobs()
        
        # Get due variants
        test_get_due_variants()
        
        # Get scheduled variants
        test_get_scheduled_variants()
    
    print("\n" + "=" * 60)
    print("✅ Module 10 Tests Complete!")
    print("=" * 60)
    print("\n📝 Note: The scheduled job will run in about 1 minute.")
    print("  Check your Discord channel to see the published post!")
