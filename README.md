# AI-Powered Content Summarizer & Researcher

A containerized full-stack web application that automates information gathering and synthesis using Django and Google Agent Kit. The platform transforms long-form articles, research papers, or web URLs into concise, actionable summaries through intelligent AI processing.

## Key Features

- **URL & Text Processing**: Submit URLs or paste text for AI-powered analysis
- **Asynchronous Processing**: Background task handling via Celery/Redis prevents UI blocking
- **Research History**: Secure dashboard to view, search, and manage past research
- **User Authentication**: Secure login system with user-specific data isolation
- **Export Capabilities**: Generate PDF reports of research results

## Tech Stack

**Backend**: Django, Django REST Framework, Celery  
**Database**: PostgreSQL  
**Message Broker**: Redis  
**AI Engine**: Google Cloud AI Platform (Vertex AI/Gemini)  
**Server**: Gunicorn + Uvicorn (ASGI)  
**Containerization**: Docker, Docker Compose  
**Frontend**: HTML/CSS/JavaScript

## Architecture

Three-layer architecture:
1. **Interface Layer**: API endpoints, task producers, state managers
2. **Domain Layer**: Celery workers, AI engine wrappers, research logic
3. **Data Layer**: PostgreSQL repositories, Redis broker, data models

All services orchestrated via Docker Compose with:
- Nginx reverse proxy
- Multi-container deployment (web, workers, database, cache)
- Docker volumes for data persistence
- Multi-stage builds for optimized images

## Quick Start

```bash
# Clone repository
git clone <repository-url>

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Launch services
docker-compose up -d

# Access application
http://localhost:80
```

## API Endpoints

- `POST /api/v1/summaries/` - Submit new research task
- `GET /api/v1/summaries/{id}/` - Check task status/retrieve result
- `GET /api/v1/summaries/` - List user research history

See API documentation at `/api/schema/swagger-ui/`

## Documentation

For complete technical specifications, architecture details, database design, and deployment strategies, refer to the [Technical Design Document](AI-Powered_Content_Summarizer___Researcher.pdf).

**Author**: Gabriel de Almeida Miki
