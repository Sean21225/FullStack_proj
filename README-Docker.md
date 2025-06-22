# Docker Setup Guide for Job Application Management System

## Prerequisites

- Docker and Docker Compose installed on your system
- Git for cloning the repository

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd <project-directory>
   ```

2. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - API Documentation: http://localhost:5000/docs
   - Database: localhost:5432

## Project Structure

```
project/
├── app/
│   ├── backend/          # FastAPI backend
│   │   ├── main.py       # Main application
│   │   ├── models.py     # Database models
│   │   ├── routers/      # API routes
│   │   └── Dockerfile    # Backend Docker config
│   └── frontend/         # React frontend
│       ├── src/          # React source code
│       ├── public/       # Static files
│       └── Dockerfile    # Frontend Docker config
├── docker-compose.yml    # Multi-service configuration
└── README-Docker.md      # This file
```

## Services

### Database (PostgreSQL)
- **Container**: `job_app_db`
- **Port**: 5432
- **Database**: `jobapp_db`
- **User**: `jobapp_user`
- **Password**: `jobapp_password`

### Backend (FastAPI)
- **Container**: `job_app_backend`
- **Port**: 5000 (maps to container port 8000)
- **Health Check**: `/health` endpoint
- **API Docs**: `/docs` endpoint

### Frontend (React + Nginx)
- **Container**: `job_app_frontend`
- **Port**: 3000 (maps to container port 80)
- **Build**: Multi-stage build with Node.js and Nginx

## Common Issues and Solutions

### 1. npm ci Error (Fixed)
**Error**: `npm ci` command fails with missing package-lock.json
**Solution**: Updated Dockerfile to use `npm install` instead of `npm ci --only=production`

### 2. Port Conflicts
**Error**: `Address already in use`
**Solution**: Stop existing services or change ports in docker-compose.yml

### 3. Database Connection Issues
**Error**: Backend can't connect to database
**Solution**: Ensure database service is healthy before starting backend (handled by depends_on)

### 4. CORS Issues
**Error**: Frontend can't access backend API
**Solution**: Backend includes CORS middleware for localhost:3000

## Environment Variables

The application uses the following environment variables (automatically set in Docker Compose):

### Backend
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `ALGORITHM`: JWT algorithm (HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

### Frontend
- `REACT_APP_API_URL`: Backend API URL (http://localhost:5000)

## Development vs Production

### Development Mode
Current configuration is optimized for development with:
- Volume mounts for live code changes
- Development servers with hot reload
- Exposed database port for direct access

### Production Considerations
For production deployment, consider:
- Remove volume mounts
- Use production-optimized images
- Secure database access (no exposed ports)
- Use environment-specific secrets
- Configure reverse proxy/load balancer

## Commands

### Start services
```bash
docker-compose up --build
```

### Start in background
```bash
docker-compose up -d --build
```

### Stop services
```bash
docker-compose down
```

### View logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs database
```

### Rebuild specific service
```bash
docker-compose build backend
docker-compose build frontend
```

### Access container shell
```bash
# Backend container
docker exec -it job_app_backend bash

# Database container
docker exec -it job_app_db psql -U jobapp_user -d jobapp_db
```

## Health Checks

All services include health checks:
- **Database**: PostgreSQL ready check
- **Backend**: HTTP health endpoint
- **Frontend**: Built-in Nginx health

Check service status:
```bash
docker-compose ps
```

## Data Persistence

Database data is persisted using Docker volumes:
- Volume name: `postgres_data`
- Data persists between container restarts

To reset database:
```bash
docker-compose down -v  # Remove volumes
docker-compose up --build
```

## Troubleshooting

### Check service logs
```bash
docker-compose logs -f [service_name]
```

### Restart specific service
```bash
docker-compose restart [service_name]
```

### Clean rebuild
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Database connection test
```bash
docker exec -it job_app_db pg_isready -U jobapp_user -d jobapp_db
```