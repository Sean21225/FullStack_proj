# 🗂 Job Application Management Backend

A comprehensive FastAPI backend system for managing job applications, resumes, and user accounts — powered with external AI services and clean architecture.

## 🚀 Features

### 🔐 Core Functionality
- **User Authentication**: Secure JWT-based signup, login, and profile management
- **Resume Management**: Full CRUD with versioning
- **Job Application Tracking**: Track job applications and status
- **User Dashboard**: Analytics and statistics on job search progress

### 🔗 External Integrations
- **Resume Optimization**: AI-powered tailoring via external service
- **LinkedIn Scraper**: Fetch jobs and companies from LinkedIn
- **Analytics**: Success rate tracking, trend insights

### ⚙️ Technical Highlights
- **REST API**: Fully documented via OpenAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Security**: Password hashing, JWT auth, input validation
- **Testing**: Unit & integration tests with pytest and httpx
- **Design**: OOP and SOLID-compliant architecture

## 📦 Requirements

- Python 3.8+
- PostgreSQL 12+
- Virtual environment (recommended)

## 🔧 Quick Setup

### 1. Clone and Setup Environment
```bash
git clone <repository-url>
cd job-application-backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary "pydantic[email]" python-jose passlib[bcrypt] python-multipart requests pytest httpx email-validator
```

### 2. Configure Environment Variables
Create a `.env` file in the root with:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/job_db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Run the Server
```bash
python main.py
```

Visit the interactive docs at:
👉 **http://localhost:5000/docs**

## 🧪 Running Tests

```bash
# Run comprehensive test suite
python app_test.py

# Run integration tests
python integration_test.py

# Run unit tests
pytest tests/ -v
```

## 🐳 Run with Docker

```bash
docker build -t job-app-backend .
docker run -d -p 5000:5000 job-app-backend
```

## 🗂 Project Structure

```
.
├── routers/
│   ├── auth.py          # Authentication endpoints
│   ├── applications.py  # Job application CRUD
│   ├── resumes.py      # Resume management
│   └── services.py     # External service integrations
├── services/
│   ├── resume_optimizer.py  # AI resume optimization
│   └── linkedin_scraper.py  # LinkedIn job scraping
├── tests/
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
├── main.py             # FastAPI application entry point
├── models.py           # Database models
├── schemas.py          # Pydantic schemas
├── auth.py             # Authentication utilities
├── database.py         # Database configuration
├── app_test.py         # Comprehensive API tests
├── integration_test.py # End-to-end tests
├── Dockerfile          # Docker configuration
└── README.md
```

## 📚 API Documentation

The API provides comprehensive endpoints for:

- **Authentication** (`/auth/`): User signup, login, token refresh
- **User Management** (`/user/`): Profile management and statistics
- **Resume Management** (`/resume/`): CRUD operations with soft delete
- **Applications** (`/applications/`): Job application tracking with filtering
- **External Services** (`/services/`): Resume optimization and LinkedIn integration

### Key Endpoints:
- `GET /health` - Health check
- `POST /auth/signup` - User registration
- `POST /auth/login` - User authentication
- `GET /user/profile` - Get user profile
- `POST /resume` - Create resume
- `GET /applications` - List applications with filters
- `POST /services/resume/optimize` - Optimize resume
- `GET /services/linkedin/jobs` - Search LinkedIn jobs

Visit `/docs` for interactive API documentation with request/response examples.

## 🛡️ Security Features

- JWT token-based authentication
- Password hashing with bcrypt
- Input validation with Pydantic
- SQL injection protection via SQLAlchemy ORM
- CORS configuration for secure cross-origin requests

## 🔧 Development

### Setting Up Development Environment
```bash
# Install development dependencies
pip install -r requirements.txt

# Run in development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
