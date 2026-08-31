# Social Media Studio

**Transform one blog post into a full social media campaign.**

## Overview

Social Media Studio is a backend service that takes a single blog post and generates platform-specific variants for multiple social media platforms. It includes a review workflow, scheduling, and idempotent publishing with failure recovery.

## Features

* Blog Post Ingestion - Accept posts via URL or pasted text
* Variant Generation - Create platform-specific versions for Twitter, LinkedIn, and Discord
* Constraint Validation - Enforce platform rules such as length, tone, and hashtags
* Review Workflow - Approve, reject, or edit variants before publishing
* Publisher Adapter Architecture - Clean interface for multiple platforms
* Idempotent Publishing - Prevent duplicate publishes with idempotency keys
* Durable Scheduling - Scheduler survives restarts with persistent job store
* Publish History - Track all publish attempts with filtering
* Mock Publishers - Test without real platform accounts

## Tech Stack

* **Framework:** FastAPI
* **Database:** SQLite (development) / PostgreSQL (production)
* **ORM:** SQLAlchemy
* **Migrations:** Alembic
* **Scheduler:** APScheduler
* **Real Publisher:** Discord Webhook
* **Containerization:** Docker + Docker Compose

## Quick Start

### Prerequisites

* Python 3.11+
* Docker (optional)

### Local Development

#### 1. Clone the repository

```bash
git clone <your-repo-url>
cd flyrank-capstone-social-studio
```

#### 2. Create a virtual environment

```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

#### 4. Set up environment variables

Copy the example environment file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Then edit the `.env` file with your configuration.

Example:

```env
DATABASE_URL=sqlite:///./social_media_studio.db
DISCORD_WEBHOOK_URL=your_discord_webhook_url_here
```

#### 5. Run the application

```bash
uvicorn app.main:app --reload
```

#### 6. Access the API

* API: `http://localhost:8000`
* Documentation: `http://localhost:8000/docs`
* Health Check: `http://localhost:8000/health`

## Docker

### 1. Build and run

```bash
docker-compose up -d
```

### 2. Check logs

```bash
docker-compose logs -f
```

### 3. Stop

```bash
docker-compose down
```

## API Endpoints

### Posts

* `POST /posts/ingest` - Ingest a blog post using text or URL
* `GET /posts` - List all posts
* `GET /posts/{id}` - Get a specific post
* `DELETE /posts/{id}` - Delete a post

### Variants

* `POST /posts/{id}/variants/generate` - Generate variants for a post
* `GET /posts/{id}/variants` - Get variants for a post
* `GET /variants/{id}` - Get a specific variant
* `PATCH /variants/{id}/content` - Update variant content
* `PATCH /variants/{id}/status` - Update variant status
* `DELETE /variants/{id}` - Delete a variant

### Review Workflow

* `POST /variants/{id}/approve` - Approve a variant
* `POST /variants/{id}/reject` - Reject a variant

### Publishing

* `POST /publish/{id}` - Publish a variant with idempotency
* `POST /publish/{id}/idempotent` - Perform an idempotent publish
* `GET /publishers` - List available publishers

### Scheduling

* `POST /scheduler/schedule/{id}` - Schedule a variant
* `GET /scheduler/jobs` - List scheduled jobs
* `DELETE /scheduler/jobs/{id}` - Cancel a scheduled job

### History

* `GET /history` - Get publish history with filters
* `GET /history/stats` - Get publishing statistics
* `GET /history/timeline` - Get activity timeline

## Configuration

Environment variables used by the application:

| Variable              | Description                        | Default                              |
| --------------------- | ---------------------------------- | ------------------------------------ |
| `DATABASE_URL`        | Database connection URL            | `sqlite:///./social_media_studio.db` |
| `DISCORD_WEBHOOK_URL` | Discord webhook URL for publishing | Optional                             |

## Architecture

```text
User Input (URL/Text)
         ↓
   Blog Post Ingestion
         ↓
   Variant Generation
         ↓
   Constraint Validation
         ↓
   Review Workflow
         ↓
   Schedule/Publish
         ↓
   Publisher Adapter
         ↓
   Platform (Discord/Mock)
```

## Testing

Run the test suite using:

```bash
python test_module13.py
```

## Evidence

See `EVIDENCE.md` for proof of all project requirements.

## Build Log

See `BUILDLOG.md` for the AI usage and development log.

## License

This project is for educational purposes as part of the FlyRank Backend Internship.
