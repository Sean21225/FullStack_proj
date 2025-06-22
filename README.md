# Job Application Management System

A comprehensive full-stack application for managing job applications, resumes, and user accounts with external service integrations.

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │    Database     │
│   (React)       │◄──►│   (FastAPI)     │◄──►│  (PostgreSQL)   │
│   Port: 3000    │    │   Port: 5000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Features

### Frontend (React)
- **User Authentication**: Secure login/signup with JWT tokens
- **Dashboard**: Overview of applications and statistics
- **Application Management**: Create, edit, delete, and filter job applications
- **Resume Management**: Store and manage multiple resume versions
- **User Profile**: Update account information
- **Responsive Design**: Works on desktop and mobile devices

### Backend (FastAPI)
- **RESTful API**: Comprehensive endpoints for all functionality
- **Authentication**: JWT-based authentication with bcrypt password hashing
- **Database Integration**: PostgreSQL with SQLAlchemy ORM
- **Input Validation**: Pydantic schemas for data validation
- **API Documentation**: Automatic OpenAPI/Swagger documentation
- **External Services**: Resume optimization and LinkedIn job scraping

### Database
- **User Management**: Secure user accounts and profiles
- **Resume Storage**: Multiple resume versions per user
- **Application Tracking**: Job applications with status management
- **Relational Design**: Proper foreign key relationships and constraints

## Quick Start

### Option 1: Docker Compose (Recommended)

1. **Clone and navigate to the project directory**
   ```bash
   git clone <repository-url>
   cd job-application-management
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - API Documentation: http://localhost:5000/docs

### Option 2: Manual Setup

#### Backend Setup
1. **Navigate to backend directory**
   ```bash
   cd app/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost:5432/jobapp"
   export SECRET_KEY="your-secret-key"
   export ALGORITHM="HS256"
   export ACCESS_TOKEN_EXPIRE_MINUTES="30"
   ```

5. **Start the backend server**
   ```bash
   python main.py
   ```

#### Frontend Setup
1. **Navigate to frontend directory**
   ```bash
   cd app/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

## API Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh JWT token

### User Management
- `GET /user/profile` - Get user profile
- `PUT /user/profile` - Update user profile

### Resume Management
- `GET /resume` - List user resumes
- `POST /resume` - Create new resume
- `GET /resume/{id}` - Get specific resume
- `PUT /resume/{id}` - Update resume
- `DELETE /resume/{id}` - Delete resume

### Application Management
- `GET /applications` - List applications (with filtering)
- `POST /applications` - Create new application
- `GET /applications/{id}` - Get specific application
- `PUT /applications/{id}` - Update application
- `DELETE /applications/{id}` - Delete application
- `GET /applications/statistics/summary` - Get application statistics

### External Services
- `POST /services/optimize-resume` - Resume optimization
- `GET /services/linkedin/jobs` - LinkedIn job search
- `GET /services/linkedin/company` - LinkedIn company data

## Development

### Frontend Development
- Built with React 18 and React Router
- Uses Axios for API communication
- Context API for state management
- Responsive CSS Grid and Flexbox layout

### Backend Development
- FastAPI with async/await support
- SQLAlchemy ORM with PostgreSQL
- Pydantic for data validation
- JWT authentication with secure password hashing

### Database Schema
```sql
Users (user_id, username, email, password_hashed, created_at, is_active)
Resumes (resume_id, user_id, title, content, created_at, updated_at, is_active)
Applications (application_id, user_id, resume_id, job_title, company, status, created_at, updated_at, job_description, application_url, notes)
```

## Environment Variables

### Backend
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing secret
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration (default: 30)

### Frontend
- `REACT_APP_API_URL`: Backend API URL (default: http://localhost:5000)

## Testing

### Backend Tests
```bash
cd app/backend
python -m pytest tests/
python integration_test.py
```

### Frontend Tests
```bash
cd app/frontend
npm test
```

## Production Deployment

1. **Update environment variables** for production
2. **Configure CORS** in backend for your domain
3. **Set up SSL/TLS** certificates
4. **Use production database** with proper backups
5. **Configure reverse proxy** (nginx recommended)

## Security Features

- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: Secure token-based authentication
- **Input Validation**: Comprehensive data validation
- **SQL Injection Prevention**: SQLAlchemy ORM
- **CORS Configuration**: Configurable cross-origin requests

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the repository or contact the development team.