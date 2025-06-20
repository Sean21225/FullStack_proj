# Docker Setup Guide

## Fixed Issues
- ✅ JWT import error: Changed from `import jwt` to `from jose import jwt`
- ✅ Updated Dockerfile to use port 8000 as specified
- ✅ Created proper requirements file for Docker
- ✅ Fixed exception handling for JWT tokens

## Build and Run Instructions

1. **Build the Docker image:**
   ```bash
   docker build -t proj_backend .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 proj_backend
   ```

3. **Test the API:**
   ```bash
   curl http://localhost:8000/health
   ```

## Environment Variables for Production

For production deployment, set these environment variables:

```bash
docker run -p 8000:8000 \
  -e DATABASE_URL="your_postgres_connection_string" \
  -e JWT_SECRET_KEY="your_secure_secret_key" \
  -e ACCESS_TOKEN_EXPIRE_MINUTES="30" \
  proj_backend
```

## API Endpoints

- **Health Check:** `GET /health`
- **API Documentation:** `GET /docs`
- **User Registration:** `POST /auth/signup`
- **User Login:** `POST /auth/login`
- **Create Resume:** `POST /resume`
- **Create Application:** `POST /applications`
- **Get Applications:** `GET /applications`
- **Get Statistics:** `GET /applications/statistics/summary`

## Database Configuration

The application expects a PostgreSQL database. Set the `DATABASE_URL` environment variable with your connection string in the format:
```
postgresql://username:password@host:port/database_name
```