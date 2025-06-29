# Job Application Management Platform

## Overview

A complete full-stack job application management platform with FastAPI backend and React frontend. The system provides comprehensive job tracking, resume management with intelligent optimization, user authentication, and a modern web interface for job seekers to manage their entire application process.

## System Architecture

**Backend Framework**: FastAPI with automatic OpenAPI documentation
- RESTful API design with proper HTTP status codes
- Async/await support for improved performance
- Built-in request/response validation with Pydantic

**Database Layer**: PostgreSQL with SQLAlchemy ORM
- Relational database design with proper foreign key relationships
- Connection pooling and session management
- Database migrations through SQLAlchemy metadata

**Authentication**: JWT-based authentication with bcrypt password hashing
- Secure token-based authentication
- Password hashing using industry-standard bcrypt
- Role-based access control for protected endpoints

## Key Components

### Database Models
- **User**: Core user entity with authentication credentials and profile data
- **Resume**: User-owned resume documents with versioning support
- **Application**: Job application tracking with status management
- Proper relationships and cascade delete operations

### API Routers
- **Auth Router** (`/auth`): User registration and login endpoints
- **Users Router** (`/user`): Profile management operations
- **Resumes Router** (`/resume`): Resume CRUD operations
- **Applications Router** (`/applications`): Job application management
- **Services Router** (`/services`): External service integrations

### External Services
- **Resume Optimizer**: AI-powered resume tailoring and optimization
- **LinkedIn Scraper**: Job and company data extraction from LinkedIn

### Security Features
- JWT token authentication with configurable expiration
- Password hashing with bcrypt and salt
- Input validation and sanitization
- CORS middleware for cross-origin requests

## Data Flow

1. **User Registration**: New users sign up with username, email, and password
2. **Authentication**: Users login to receive JWT access tokens
3. **Resume Management**: Users create and manage multiple resume versions
4. **Job Applications**: Users track applications with status updates and notes
5. **External Services**: Integration with resume optimization and job scraping APIs
6. **Analytics**: Basic dashboard functionality for application tracking

## External Dependencies

### Core Dependencies
- `fastapi`: Web framework and API development
- `uvicorn`: ASGI server for FastAPI applications
- `sqlalchemy`: ORM for database operations
- `psycopg2-binary`: PostgreSQL database driver
- `pydantic`: Data validation and serialization
- `python-jose`: JWT token handling
- `passlib`: Password hashing utilities

### Service Dependencies
- `requests`: HTTP client for external API calls
- `httpx`: Async HTTP client for testing
- `pytest`: Testing framework with async support

### Development Dependencies
- `email-validator`: Email format validation
- `python-multipart`: File upload support

## Deployment Strategy

### Docker Support
- Multi-stage Dockerfile with Python 3.11 slim base image
- Health check endpoints for container monitoring
- Non-root user configuration for security
- Optimized layer caching for faster builds

### Docker Compose
- PostgreSQL database service with health checks
- Web service with proper dependency management
- Volume management for data persistence
- Environment variable configuration

### Production Considerations
- Environment-based configuration management
- Database connection pooling and retry logic
- Logging configuration with structured output
- Error handling with proper HTTP status codes

## Changelog
- June 22, 2025. Initial setup
- June 22, 2025. Added React frontend with full integration to FastAPI backend

## Recent Changes
- Created complete React frontend with authentication, dashboard, applications management, resumes management, and user profile
- Integrated React frontend with existing FastAPI backend
- Fixed data display issues across all frontend components (resumes, applications, statistics)
- Reorganized project structure for Docker deployment with proper app/backend and app/frontend directories
- Fixed Docker configuration issues for PyCharm deployment
- Updated frontend Dockerfile to use npm install instead of npm ci
- Fixed port mappings and removed obsolete docker-compose version field
- Created comprehensive Docker setup guides for development and production
- Fixed database connection issues by creating PostgreSQL database and updating environment variables
- Backend now running successfully on port 5000 with full functionality working
- Created comprehensive PyCharm setup guide for local development
- All frontend and backend functionality working correctly in both Docker and Replit environments
- **June 29, 2025**: Replaced OpenAI API dependency with free rule-based resume optimization service
- Implemented completely free resume analysis and optimization that works without any API costs
- Resume optimization now uses intelligent rule-based analysis for scoring, suggestions, and content improvement
- **June 29, 2025**: Successfully tested complete frontend-backend integration with free optimization service
- Verified resume optimization feature works seamlessly through React interface without external API dependencies
- Created comprehensive testing framework demonstrating all optimization capabilities working correctly
- **June 29, 2025**: Fixed resume optimization scoring and content expansion issues
- Improved scoring algorithm to properly cap at 100% and provide realistic assessments
- Enhanced content optimization to expand very short resumes with professional structure
- Added intelligent suggestions tailored to content length and quality
- **June 29, 2025**: Reconfigured application deployment for Replit environment
- Frontend now runs on port 5000 (accessible) with backend API on port 8000
- Fixed port accessibility issues and established proper frontend-backend communication

## User Preferences

Preferred communication style: Simple, everyday language.