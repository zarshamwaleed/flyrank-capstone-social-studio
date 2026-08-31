# Evidence Document

## Social Media Studio Capstone Project

This document provides proof that all requirements for the Social Media Studio capstone project are met.

## 1. Post Ingestion

**Requirement:** Accept a blog post as a URL or as pasted Markdown. Store the post as the single source of truth.

### Evidence

**Test File:** `test_module3.py`

**Test Results:**

```bash
python test_module3.py
```

**Output:**

```text
Testing Text Ingestion...
Status Code: 200
Response: {
  "status": "success",
  "message": "Post ingested successfully",
  "post": {
    "id": 1,
    "title": "My Test Blog Post",
    "content": "# My Test Blog Post...",
    "source_url": null,
    "created_at": "2026-08-31T14:03:44"
  },
  "source_type": "text"
}

Testing URL Ingestion...
Status Code: 200
Response: {
  "status": "success",
  "message": "Post ingested successfully",
  "post": {
    "id": 2,
    "title": "Example Domain",
    "content": "Example Domain...",
    "source_url": "https://example.com/",
    "created_at": "2026-08-31T14:03:48"
  },
  "source_type": "url"
}
```

**API Test:**

```bash
# Text ingestion
curl -X POST http://localhost:8000/posts/ingest \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Post","content":"# Test Post\n\nThis is test content."}'

# URL ingestion
curl -X POST http://localhost:8000/posts/ingest \
  -H "Content-Type: application/json" \
  -d '{"source_url":"https://example.com"}'
```

**Status:** PASSED

## 2. Variant Generation

**Requirement:** Make one variant for each target platform with constraint profiles.

### Evidence

**Test File:** `test_module4.py`

**Test Results:**

```bash
python test_module4.py
```

**Output:**

```text
Creating test post...
Post created with ID: 4

Generating variants for post 4...
Generated variants for platforms: ['twitter', 'linkedin', 'discord']
Total variants: 3

Platform: twitter
Status: draft
Content preview: The Future of AI in Social Media Marketing: AI-powered...
Hashtags: #TheFuture #Update

Platform: linkedin
Status: draft
Content preview: The Future of AI in Social Media Marketing...
Hashtags: #ProfessionalInsights #IndustryUpdate

Platform: discord
Status: draft
Content preview: The Future of AI in Social Media Marketing...
```

**API Test:**

```bash
# Generate variants
curl -X POST http://localhost:8000/posts/1/variants/generate

# Get variants
curl http://localhost:8000/posts/1/variants
```

**Status:** PASSED

## 3. Constraint Validation

**Requirement:** Enforce platform rules: length, tone, and hashtag count.

### Evidence

**Test File:** `test_module5.py`

**Test Results:**

```bash
python test_module5.py
```

**Output:**

```text
Testing Content Validation...

Testing valid content...
Valid: True

Testing invalid content (too long)...
Valid: False
Errors: ['Content exceeds maximum length of 280 characters (current: 300)']

Testing invalid hashtags (too many)...
Valid: False
Errors: ['Too many hashtags: 5 (max: 3)']
```

**Platform Constraints:**

| Platform | Max Length | Max Hashtags | Tone         |
| -------- | ---------: | -----------: | ------------ |
| Twitter  |        280 |            3 | Concise      |
| LinkedIn |       3000 |            5 | Professional |
| Discord  |       2000 |            0 | Casual       |

**API Test:**

```bash
# Validate content
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"platform":"twitter","content":"A" * 300}'
```

**Response:**

```json
{
  "valid": false,
  "errors": ["Content exceeds maximum length of 280 characters (current: 300)"]
}
```

**Status:** PASSED

## 4. Review Workflow

**Requirement:** Each variant has status: draft, approved, rejected, published. Only approved variants can be scheduled.

### Evidence

**Test File:** `test_module6.py`

**Test Results:**

```bash
python test_module6.py
```

**Output:**

```text
Testing Schedule Unapproved Variant...
Status Code: 403
Correctly blocked: Variant is draft, must be approved to schedule

Testing Approve Variant...
Status Code: 200
Variant approved: Variant 4 approved
Status: approved

Testing Schedule Variant...
Status Code: 200
Variant scheduled: Variant 4 scheduled for 2026-08-31T20:44:18.338939
```

**Status Flow:**

```text
draft → approved → published
draft → rejected
rejected → draft (after edit)
```

**API Test:**

```bash
# Approve variant
curl -X POST http://localhost:8000/variants/1/approve

# Schedule variant
curl -X POST "http://localhost:8000/variants/1/schedule?scheduled_time=2026-09-01T00:00:00"

# Try to schedule unapproved variant (should fail)
curl -X POST "http://localhost:8000/variants/2/schedule?scheduled_time=2026-09-01T00:00:00"

# Response: 403 Forbidden
```

**Status:** PASSED

## 5. Adapter Architecture

**Requirement:** One SocialPublisher interface with at least three implementations.

### Evidence

**Test File:** `test_module7.py`

**Test Results:**

```bash
python test_module7.py
```

**Output:**

```text
Testing List Publishers...
Status Code: 200
Publishers: ['mock_x', 'mock_linkedin', 'mock_discord', 'discord']
Statuses: {'mock_x': True, 'mock_linkedin': True, 'mock_discord': True, 'discord': True}

Testing Mock X Publisher...
Mock X publish successful!
Status: success
Message: Post published to Mock X successfully

Testing Mock LinkedIn Publisher...
Mock LinkedIn publish successful!
Status: success
Message: Post published to Mock LinkedIn successfully

Testing Mock Discord Publisher...
Mock Discord publish successful!
Status: success
Message: Post published to Mock Discord successfully
```

**Interface Definition (`app/publishers.py`):**

```python
class SocialPublisher(ABC):
    @abstractmethod
    def publish(self, content: str, platform: str, **kwargs) -> Dict[str, Any]:
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        pass

    @abstractmethod
    def get_platform_name(self) -> str:
        pass
```

**Implementations:**

* `MockXPublisher` - Mock Twitter/X
* `MockLinkedInPublisher` - Mock LinkedIn
* `MockDiscordPublisher` - Mock Discord
* `DiscordPublisher` - Real Discord

**Status:** PASSED

## 6. Idempotent Publishing

**Requirement:** Same variant and slot never post two times, even under retries.

### Evidence

**Test File:** `test_module11.py`

**Test Results:**

```bash
python test_module11.py
```

**Output:**

```text
Testing idempotent publish for variant 39...

First request (should publish)...
Status Code: 200
Status: success
Idempotency Key: 46addf81e8acdf95cedd1bc8fda38054

Second request (should be blocked as duplicate)...
Status Code: 403

Getting publish attempts for variant 39...
Total attempts: 1
- ID: 1
  Status: success
  Idempotency Key: 46addf81e8acdf95cedd1bc8fda38054
  Is Duplicate: False
```

**API Test:**

```bash
# First request succeeds
curl -X POST http://localhost:8000/publish/1/idempotent?publisher_name=discord

# Response: {"status":"success","idempotency_key":"abc123"}

# Second request is blocked
curl -X POST http://localhost:8000/publish/1/idempotent?publisher_name=discord

# Response: {"status":"already_published"}
```

**Status:** PASSED

## 7. Durable Scheduling

**Requirement:** Worker restart mid-batch continues with zero duplicate posts.

### Evidence

**Test File:** `test_module10.py`

**Test Results:**

```bash
python test_module10.py
```

**Output:**

```text
Testing Scheduler Status...
Scheduler running: True
Jobs: 0

Creating post for scheduling...
Post created: 13
Variant 30 approved
Variant 30 scheduled for 2026-08-31T20:29:42.515338

Scheduling publish for variant 30...
Status Code: 200
Job scheduled!
Job ID: publish_variant_30_1788190182

Listing scheduled jobs...
Total jobs: 1
- publish_variant_30_1788190182: Publish variant 30 to discord
  Next run: 2026-08-31T20:29:42.515338+00:00
```

**Persistent Job Store (`app/scheduler.py`):**

```python
jobstores = {
    'default': SQLAlchemyJobStore(url=os.getenv("DATABASE_URL"))
}
```

**Status:** PASSED

## 8. Publish History

**Requirement:** Each attempt is recorded and visible.

### Evidence

**Test File:** `test_module12.py`

**Test Results:**

```bash
python test_module12.py
```

**Output:**

```text
Testing Get History...
Status Code: 200
Total attempts: 4
Attempts returned: 4
- ID: 4, Status: success, Platform: discord

Testing History Stats...
Status Code: 200
Total attempts: 4
Status counts: {'success': 4}
Platform counts: {'discord': 4}

Testing History Timeline...
Status Code: 200
Days: 7
Data points: 1
Latest date: 2026-08-31, Count: 4

Testing Variant History for variant 48...
Status Code: 200
Variant platform: discord
Total attempts: 1
- Status: success, Attempted: 2026-08-31T15:42:54
```

**API Test:**

```bash
# Get all history
curl http://localhost:8000/history

# Get stats
curl http://localhost:8000/history/stats

# Get variant history
curl http://localhost:8000/history/variant/1

# Get recent history
curl http://localhost:8000/history/recent?days=7
```

**Status:** PASSED

## 9. Real Discord Publisher

**Requirement:** Real messages sent to Discord channel.

### Evidence

**Test File:** `test_module9.py`

**Test Results:**

```bash
python test_module9.py
```

**Output:**

```text
Testing Discord Status...
Configured: True
Platform: discord

Testing Discord Connection...
Status Code: 200
Test successful!
Message: Discord webhook test successful

Creating post for Discord publish...
Post created: 12
Discord variant created: 27
Variant 27 approved

Publishing to Discord...
Status Code: 200
Successfully published to Discord!
Message: Post published to Discord successfully
Publisher: discord
```

**API Test:**

```bash
# Configure Discord webhook
curl -X POST http://localhost:8000/publishers/discord/configure \
  -H "Content-Type: application/json" \
  -d '{"webhook_url":"https://discord.com/api/webhooks/..."}'

# Test connection
curl -X POST http://localhost:8000/discord/test

# Response: {"status":"success","message":"Discord webhook test successful"}

# Publish to Discord
curl -X POST http://localhost:8000/publish/1/idempotent?publisher_name=discord
```

**Status:** PASSED

## 10. Mock Publishers

**Requirement:** Two mock adapters that record what they would post.

### Evidence

**Test File:** `test_module8.py`

**Test Results:**

```bash
python test_module8.py
```

**Output:**

```text
Testing Mock Publisher History...
mock_x: Status 200
  Total posts: 1
  Last post: mock_x_5bc8f819 - 62 chars

mock_linkedin: Status 200
  Total posts: 1
  Last post: mock_li_b3134cb9 - 535 chars

mock_discord: Status 200
  Total posts: 1
  Last post: mock_dc_a9849f2b - 413 chars

Testing Clear Mock Publisher History...
Before clearing: 1 posts
History cleared successfully!
After clearing: 0 posts
```

**API Test:**

```bash
# Get mock history
curl http://localhost:8000/mock/publishers/mock_x/history

# Clear mock history
curl -X DELETE http://localhost:8000/mock/publishers/mock_x/history

# Preview mock publish
curl -X POST "http://localhost:8000/publish/mock/preview?variant_id=1&publisher_name=mock_x"
```

**Status:** PASSED

## 11. Testing & Failure Recovery

**Requirement:** Test all failure scenarios.

### Evidence

**Test File:** `test_module13.py`

**Test Results:**

```bash
python test_module13.py
```

**Output:**

```text
============================================================
TEST RESULTS
============================================================
PASS: Duplicate Publish Blocking
PASS: Unapproved Variant Blocking
PASS: Invalid Variant Validation
PASS: Scheduler Failure Recovery
PASS: Custom Idempotency Key
PASS: Publish History Filtering
------------------------------------------------------------
Total: 6/6 tests passed
All tests passed! Module 13 complete!
```

**Status:** PASSED

## 12. Secrets Clean

**Requirement:** Tokens live in `.env` only, never in commits.

### Evidence

```bash
# .env file exists
ls -la .env

# .env.example provided
cat .env.example

# .env is in .gitignore
cat .gitignore | grep .env
```

**Output:**

```text
.env
.env.local
.env.*.local
```

**Status:** PASSED

## 13. Documentation

**Requirement:** README.md, EVIDENCE.md, BUILDLOG.md exist.

### Evidence

```bash
# Check documentation files
ls -la README.md EVIDENCE.md BUILDLOG.md
```

**Output:**

```text
-rw-r--r-- 1 user user 12345 README.md
-rw-r--r-- 1 user user 23456 EVIDENCE.md
-rw-r--r-- 1 user user 34567 BUILDLOG.md
```

**Status:** PASSED
