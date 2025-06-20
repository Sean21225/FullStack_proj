# Job Application Management Backend

A comprehensive FastAPI backend system for managing job applications, resumes, and user authentication with external service integrations.

## 🚀 Features

### Core Functionality
- **User Authentication**: Secure JWT-based authentication with signup, login, and profile management
- **Resume Management**: Full CRUD operations for user resumes with version control
- **Job Application Tracking**: Complete application lifecycle management with status tracking
- **User Dashboard**: Statistics and analytics for job search progress

### External Integrations
- **Resume Optimization Service**: AI-powered resume tailoring and optimization
- **LinkedIn Scraper Service**: Job search and company information retrieval
- **Analytics**: Comprehensive reporting on application success rates and trends

### Technical Features
- **RESTful API**: Complete REST API with OpenAPI documentation
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Security**: Password hashing, JWT tokens, input validation
- **Testing**: Comprehensive unit and integration test suite
- **Architecture**: Object-oriented design following SOLID principles

## 📋 Requirements

- Python 3.8+
- PostgreSQL 12+
- Virtual environment (recommended)

## 🔧 Quick Setup

### 1. Clone and Setup Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run automated setup
python setup.py
