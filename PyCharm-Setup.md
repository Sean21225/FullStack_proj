# PyCharm Docker Setup Guide

## Issue Resolution

The Docker build error you encountered was due to the frontend Dockerfile using `npm ci --only=production` which requires a `package-lock.json` file. This has been fixed by changing to `npm install`.

## Fixed Issues

1. **Frontend Build Error**: Changed `npm ci --only=production` to `npm install` in `app/frontend/Dockerfile`
2. **Port Mapping**: Updated Docker Compose to properly map backend port 8000 to host port 5000
3. **Project Structure**: Organized code into `app/backend/` and `app/frontend/` directories for Docker
4. **Version Warning**: Removed obsolete `version` field from docker-compose.yml

## Setup Instructions for PyCharm

### 1. Project Structure
Ensure your project has this structure:
```
project/
├── app/
│   ├── backend/          # FastAPI backend files
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── routers/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── frontend/         # React frontend files
│       ├── src/
│       ├── public/
│       ├── package.json
│       ├── nginx.conf
│       └── Dockerfile
├── docker-compose.yml
└── README-Docker.md
```

### 2. Run in PyCharm Terminal

Open PyCharm terminal and run:

```bash
# Clean any existing containers
docker-compose down -v

# Build and start all services
docker-compose up --build
```

### 3. Expected Output

You should see:
- Database starts first and becomes healthy
- Backend builds and starts on port 5000
- Frontend builds and starts on port 3000

### 4. Access Points

After successful startup:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Docs**: http://localhost:5000/docs
- **Health Check**: http://localhost:5000/health

### 5. Development Workflow

The Docker setup includes volume mounts for development:
- Backend: `./app/backend:/app` - Live code changes
- Frontend: Uses development server with hot reload

### 6. Common Commands

```bash
# Start services
docker-compose up --build

# Start in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Reset everything (including database)
docker-compose down -v
docker-compose up --build
```

### 7. Troubleshooting

**Port Conflicts:**
```bash
# Check what's using the ports
netstat -tulpn | grep :3000
netstat -tulpn | grep :5000

# Stop conflicting services or change ports in docker-compose.yml
```

**Build Issues:**
```bash
# Clean rebuild
docker-compose down
docker system prune -f
docker-compose build --no-cache
docker-compose up
```

**Database Issues:**
```bash
# Check database health
docker-compose ps
docker-compose logs database

# Reset database
docker-compose down -v
docker-compose up --build
```

## Environment Variables

The Docker Compose automatically sets up:

**Backend:**
- `DATABASE_URL=postgresql://jobapp_user:jobapp_password@database:5432/jobapp_db`
- `SECRET_KEY=your-secret-key-change-in-production`
- `ALGORITHM=HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES=30`

**Frontend:**
- `REACT_APP_API_URL=http://localhost:5000`

## Development vs Production

This setup is configured for development. For production:
1. Remove volume mounts
2. Use production environment variables
3. Configure proper reverse proxy
4. Use secure database credentials
5. Enable HTTPS

## Testing the Setup

1. Open http://localhost:3000
2. Register a new user account
3. Login and create resumes
4. Create job applications
5. View statistics on profile page

All functionality should work correctly with the Docker setup.