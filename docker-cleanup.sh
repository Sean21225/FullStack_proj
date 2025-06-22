#!/bin/bash

# Docker cleanup script for Job Application Management System
# Run this script in PyCharm terminal to clean up existing containers

echo "Stopping and removing existing containers..."

# Stop all containers for this project
docker-compose down

# Remove any existing containers with the same names
docker rm -f job_app_backend job_app_frontend job_app_db 2>/dev/null || true

# Remove any orphaned containers
docker container prune -f

# Clean up unused networks
docker network prune -f

# Optional: Remove volumes to reset database (uncomment if needed)
# docker volume rm backendblueprint_postgres_data 2>/dev/null || true

echo "Cleanup complete! You can now run: docker-compose up --build"