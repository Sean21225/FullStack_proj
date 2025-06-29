# Job Application Management API

A comprehensive FastAPI-based backend system for managing job applications, resumes, and career optimization with integrated LinkedIn job search functionality.

## 🚀 Features

- **User Management**: Secure registration and authentication with JWT tokens
- **Resume Management**: Create, edit, and optimize resumes with AI-powered suggestions
- **Job Application Tracking**: Track applications with status updates and notes
- **LinkedIn Job Search**: Real-time job search across LinkedIn, Indeed, Glassdoor, and ZipRecruiter
- **Company Information**: Lookup company details and current job openings
- **Resume Optimization**: Free AI-powered resume analysis and improvement suggestions
- **RESTful API**: Complete REST API with automatic OpenAPI documentation

## 🏗️ Architecture

### Tech Stack
- **Framework**: FastAPI with async/await support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT with bcrypt password hashing
- **External APIs**: JSearch API (RapidAPI) for job data
- **Documentation**: Automatic OpenAPI/Swagger documentation

### Key Components
- **Models**: SQLAlchemy ORM models for Users, Resumes, and Applications
- **Routers**: Modular API endpoints organized by functionality
- **Services**: External service integrations (resume optimizer, job search)
- **Authentication**: Secure JWT-based auth with role-based access control

## 📁 Project Structure

```
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── unit_tests.py        # Unit tests for all components
│   └── requirements.txt     # Python dependencies
├── integration_test.py      # Integration tests for complete workflows
├── Dockerfile              # Docker container configuration
├── README.md               # This file
├── auth.py                 # Authentication and JWT handling
├── database.py             # Database configuration and session management
├── models.py               # SQLAlchemy database models
├── schemas.py              # Pydantic request/response schemas
├── routers/                # API route handlers
│   ├── auth.py            # Authentication endpoints
│   ├── resumes.py         # Resume management endpoints
│   ├── applications.py    # Job application endpoints
│   └── services.py        # External service endpoints
└── services/               # External service integrations
    ├── resume_optimizer.py # Free resume optimization service
    ├── jsearch_api.py      # JSearch API integration
    └── scrapingdog_linkedin.py # Alternative LinkedIn scraper
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- PostgreSQL database
- RapidAPI account (for job search functionality)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd job-application-api
   ```

2. **Install dependencies**
   ```bash
   pip install -r app/requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost:5432/jobapp"
   export SECRET_KEY="your-secret-key"
   export JSEARCH_API_KEY="your-rapidapi-key"
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

### Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t job-application-api .
   ```

2. **Run with Docker**
   ```bash
   docker run -p 8000:8000 \
     -e DATABASE_URL="postgresql://user:password@localhost:5432/jobapp" \
     -e SECRET_KEY="your-secret-key" \
     -e JSEARCH_API_KEY="your-rapidapi-key" \
     job-application-api
   ```

## 🧪 Testing

### Unit Tests
Run unit tests for individual components:
```bash
cd app
python -m pytest unit_tests.py -v
```

### Integration Tests
Run integration tests for complete workflows:
```bash
python integration_test.py
```

### Test Coverage
The test suite covers:
- Authentication workflows
- Resume CRUD operations
- Job application management
- External API integrations
- Error handling scenarios
- Performance metrics

## 📚 API Documentation

### Automatic Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

#### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Token refresh

#### Resume Management
- `GET /resume` - List user resumes
- `POST /resume` - Create new resume
- `GET /resume/{id}` - Get specific resume
- `PUT /resume/{id}` - Update resume
- `DELETE /resume/{id}` - Delete resume

#### Job Applications
- `GET /applications` - List applications
- `POST /applications` - Create application
- `GET /applications/{id}` - Get specific application
- `PUT /applications/{id}` - Update application
- `DELETE /applications/{id}` - Delete application
- `GET /applications/statistics/summary` - Get application statistics

#### External Services
- `POST /services/optimize-resume` - Optimize resume content
- `GET /services/api/suggestions/jobs` - Search for jobs
- `GET /services/api/suggestions/companies` - Get company information

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing secret key
- `JSEARCH_API_KEY`: RapidAPI key for job search
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT token expiration (default: 30)

### Database Schema
The application uses PostgreSQL with the following main tables:
- **users**: User accounts and authentication
- **resumes**: User resume documents
- **applications**: Job application tracking

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt with salt for password security
- **Input Validation**: Pydantic schemas for request validation
- **CORS Support**: Configurable cross-origin resource sharing
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection

## 🚀 Deployment

### Production Considerations
- Use environment-based configuration
- Set up database connection pooling
- Configure logging and monitoring
- Use reverse proxy (nginx) for static files
- Set up SSL/TLS certificates

### Health Checks
The application includes health check endpoints:
- `GET /health` - System health status
- Docker health checks for container monitoring

## 🤝 Contributing

1. Follow SOLID principles for object-oriented design
2. Use Pydantic for data validation
3. Include comprehensive tests for new features
4. Update documentation for API changes
5. Follow PEP 8 style guidelines

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**
- Verify PostgreSQL is running
- Check DATABASE_URL environment variable
- Ensure database exists and user has permissions

**API Key Error**
- Verify JSEARCH_API_KEY is set correctly
- Check RapidAPI subscription status
- Ensure API key has proper permissions

**Authentication Error**
- Verify SECRET_KEY is set
- Check token expiration settings
- Ensure proper request headers

## 📞 Support

For support and questions:
- Check the API documentation at `/docs`
- Review test cases for usage examples
- Create an issue for bug reports or feature requests