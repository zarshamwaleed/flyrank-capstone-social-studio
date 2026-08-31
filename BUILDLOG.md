# Build Log

## Social Media Studio Capstone Project

**Project:** Social Media Studio
**Track:** Backend
**Repository:** flyrank-capstone-social-studio
**Status:** Complete

## Development Overview

This document tracks the development process, AI usage, and lessons learned during the Social Media Studio capstone project.

## Module Development Timeline

### Module 1: Project Setup + Virtual Environment

**Status:** Complete
**Time:** Approximately 1 hour

**What Was Built:**

* Project folder structure
* Python virtual environment
* FastAPI application with health endpoints
* Basic server setup

**AI Usage:** Helped with project structure and initial setup commands.

**Challenges:** None

### Module 2: Database Setup

**Status:** Complete
**Time:** Approximately 2 hours

**What Was Built:**

* PostgreSQL with Docker, later switched to SQLite
* SQLAlchemy ORM configuration
* Database models: Post, Variant, PublishAttempt
* Alembic migrations

**AI Usage:** Helped with SQLAlchemy configuration and Alembic troubleshooting.

**Challenges:** PostgreSQL connection issues, so SQLite was used for development.

### Module 3: Blog Post Ingestion

**Status:** Complete
**Time:** Approximately 2 hours

**What Was Built:**

* Post ingestion via text and URL
* URL fetching with content extraction
* HTML parsing for title and content
* Database storage

**AI Usage:** Helped design URL fetching and text extraction.

**Challenges:** HTML parsing for clean text extraction.

### Module 4: Variant Generation

**Status:** Complete
**Time:** Approximately 3 hours

**What Was Built:**

* Platform-specific generators for Twitter, LinkedIn, and Discord
* Content extraction and summarization
* Hashtag generation
* Key point extraction

**AI Usage:** Helped design platform-specific generators.

**Challenges:** Handling the Twitter 280-character limit.

### Module 5: Constraint Validation

**Status:** Complete
**Time:** Approximately 2 hours

**What Was Built:**

* Content length validation
* Hashtag count validation
* Tone detection
* Validation API endpoint

**AI Usage:** Helped design validation logic.

**Challenges:** Tone detection accuracy.

### Module 6: Review Workflow

**Status:** Complete
**Time:** Approximately 2 hours

**What Was Built:**

* Status workflow: draft → approved → published
* Approve endpoint
* Reject endpoint with reason
* Schedule blocking for unapproved variants

**AI Usage:** Helped design the status workflow.

**Challenges:** Blocking unapproved variants from scheduling.

### Module 7: Publisher Adapter Architecture

**Status:** Complete
**Time:** Approximately 3 hours

**What Was Built:**

* SocialPublisher interface
* Publisher factory pattern
* Mock X publisher
* Mock LinkedIn publisher
* Real Discord publisher

**AI Usage:** Helped design the adapter pattern.

**Challenges:** Route ordering for endpoints.

### Module 8: Mock Publishers Testing

**Status:** Complete
**Time:** Approximately 2 hours

**What Was Built:**

* Mock publisher history
* History clearing
* Statistics endpoints
* Preview functionality

**AI Usage:** Helped design history endpoints.

**Challenges:** Route ordering for the `/all/history` endpoint.

### Module 9: Real Discord Publisher

**Status:** Complete
**Time:** Approximately 2 hours

**What Was Built:**

* Discord webhook integration
* Webhook configuration endpoint
* Connection testing
* Error handling

**AI Usage:** Helped with Discord webhook integration.

**Challenges:** Webhook configuration and testing.

### Module 10: Scheduling

**Status:** Complete
**Time:** Approximately 3 hours

**What Was Built:**

* APScheduler integration
* Persistent job store
* Job scheduling endpoint
* Job cancellation endpoint
* Due variants detection

**AI Usage:** Helped with APScheduler integration.

**Challenges:** Persistent job store configuration.

### Module 11: Idempotency

**Status:** Complete
**Time:** Approximately 2 hours

**What Was Built:**

* Idempotency key generation
* Duplicate detection
* Publish attempt tracking
* Custom idempotency keys
* Retry logic

**AI Usage:** Helped design idempotency keys.

**Challenges:** Database schema updates.

### Module 12: Publish History

**Status:** Complete
**Time:** Approximately 2 hours

**What Was Built:**

* History listing with filters
* Statistics endpoint
* Timeline endpoint
* Variant history
* Platform history

**AI Usage:** Helped design history endpoints.

**Challenges:** Import issues for the Variant model.

### Module 13: Testing & Failure Recovery

**Status:** Complete
**Time:** Approximately 3 hours

**What Was Built:**

* Duplicate publish blocking test
* Unapproved variant blocking test
* Invalid variant validation test
* Scheduler failure recovery test
* Custom idempotency key test
* Publish history filtering test

**AI Usage:** Helped design the comprehensive test suite.

**Challenges:** Test timeout handling.

### Module 14: Docker & Final Documentation

**Status:** Complete
**Time:** Approximately 2 hours

**What Was Built:**

* Dockerfile
* Docker Compose
* `.dockerignore`
* README.md
* EVIDENCE.md
* BUILDLOG.md

**AI Usage:** Helped with Docker configuration.

**Challenges:** None

## AI Usage Summary

### Where AI Helped

1. **Project Structure:** Helped organize the project and suggest best practices.
2. **Code Generation:** Generated boilerplate code for models, schemas, and endpoints.
3. **Error Debugging:** Helped identify and fix syntax, import, and routing errors.
4. **Design Patterns:** Suggested appropriate patterns such as adapter, factory, and service.
5. **Documentation:** Helped generate README, EVIDENCE, and BUILDLOG documentation.

### Where AI Was Wrong

1. **Route Ordering:** Initially suggested an incorrect order for `/mock/publishers/all/history`.
2. **Database Schema:** Required adjustments for SQLite compatibility.
3. **Test Timeouts:** Initially set timeouts too short for scheduler tests.
4. **Import Statements:** Added imports with syntax errors.
5. **PostgreSQL Setup:** Suggested an approach that did not work on Windows.

### Corrections Made

1. Fixed route ordering for mock publisher endpoints.
2. Switched from PostgreSQL to SQLite for development.
3. Extended test timeouts from 30 seconds to 45 seconds for scheduler tests.
4. Fixed import statements with proper newlines.
5. Added missing imports for the Variant model.
6. Used Docker's `host.docker.internal` for database connections.

## Lessons Learned

### 1. Route Ordering in FastAPI

FastAPI matches routes in order. Specific routes must come before parameterized routes.

```python
# WRONG - /all/history can match {publisher_name}/history
@app.get("/mock/publishers/{publisher_name}/history")
@app.get("/mock/publishers/all/history")

# CORRECT - /all/history is matched first
@app.get("/mock/publishers/all/history")
@app.get("/mock/publishers/{publisher_name}/history")
```

### 2. Database Flexibility

SQLite is useful for development, while PostgreSQL is better suited for production. The application supports both.

### 3. Idempotency is Critical

Idempotency keys prevent duplicate publishes and are essential for production systems where retries are common.

### 4. Testing Failure Scenarios

Testing edge cases such as duplicate publishes, unapproved variants, and scheduler failures helps catch critical bugs early.

### 5. Adapter Pattern

The adapter pattern makes the system extensible. Adding a new platform only requires implementing the `SocialPublisher` interface.

### 6. Docker Development

Using `host.docker.internal` for connecting to host services from Docker containers is useful when developing on Windows.

## Code Quality

### File Count

* **Total Files:** 25+
* **Python Files:** 15
* **Configuration Files:** 5
* **Documentation Files:** 3

### Test Coverage

* **Tests:** 6, all passing
* **Coverage Areas:** Idempotency, authorization, validation, scheduling, error handling, and history

### API Endpoints

* **Total:** 30+
* **Categories:** Posts, Variants, Review, Publishing, Scheduling, History, and Mock Publishers

## Final Thoughts

The Social Media Studio project demonstrates a publishing system with:

* **Clean Architecture:** Separation of concerns with services, models, and adapters
* **Robust Error Handling:** Graceful handling of failures and edge cases
* **Failure Recovery:** Idempotency and durable scheduling for reliability
* **Comprehensive Testing:** 6 tests covering critical failure scenarios
* **Real Platform Integration:** Discord webhook publishing
* **Containerization:** Docker and Docker Compose support

The adapter pattern and idempotency are particularly important learnings for real-world applications. The project has been developed with the required features, testing, documentation, and deployment configuration.

## Key Metrics

| Metric        | Value              |
| ------------- | ------------------ |
| Modules       | 14                 |
| API Endpoints | 30+                |
| Tests         | 6 (all passing)    |
| Lines of Code | Approximately 3000 |
| Files         | 25+                |

**Built with AI assistance as part of the FlyRank Backend Internship.**
