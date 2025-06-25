# PyCharm Setup Guide for Job Application Management System

## Prerequisites

1. **PyCharm Professional** (recommended) or PyCharm Community Edition
2. **Python 3.11** installed on your system
3. **Node.js 18+** for the React frontend
4. **PostgreSQL** database (local installation or Docker)

## Project Setup in PyCharm

### 1. Clone/Open Project
```bash
# If cloning from repository
git clone <your-repo-url>
cd job-application-management

# Or simply open the existing project folder in PyCharm
```

### 2. Python Environment Setup

#### Option A: Virtual Environment (Recommended)
1. Open PyCharm and load the project
2. Go to `File` → `Settings` → `Project` → `Python Interpreter`
3. Click the gear icon → `Add...`
4. Select `Virtualenv Environment` → `New environment`
5. Set Base interpreter to Python 3.11
6. Location: `./venv` (in your project directory)
7. Click `OK`

#### Option B: Conda Environment
1. Create conda environment:
```bash
conda create -n job-app python=3.11
conda activate job-app
```
2. In PyCharm: `File` → `Settings` → `Project` → `Python Interpreter`
3. Select the conda environment you just created

### 3. Install Python Dependencies

Open PyCharm terminal and run:
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic[email] python-jose passlib[bcrypt] python-multipart requests pytest httpx email-validator
```

### 4. Database Setup

#### Option A: Local PostgreSQL
1. Install PostgreSQL locally
2. Create a database:
```sql
CREATE DATABASE job_applications;
CREATE USER job_app_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE job_applications TO job_app_user;
```

#### Option B: Docker PostgreSQL
Create `docker-compose.yml` in project root:
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: job_applications
      POSTGRES_USER: job_app_user
      POSTGRES_PASSWORD: your_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Run: `docker-compose up -d`

### 5. Environment Variables

Create `.env` file in project root:
```env
DATABASE_URL=postgresql://job_app_user:your_password@localhost:5432/job_applications
SECRET_KEY=your-secret-key-here-make-it-long-and-secure
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 6. PyCharm Run Configurations

#### Backend (FastAPI) Configuration
1. `Run` → `Edit Configurations...`
2. Click `+` → `Python`
3. **Name**: `FastAPI Backend`
4. **Script path**: `/path/to/your/project/main.py`
5. **Working directory**: `/path/to/your/project`
6. **Environment variables**: Add your `.env` variables or check "Load from .env file"
7. Click `OK`

#### Frontend (React) Configuration
1. `Run` → `Edit Configurations...`
2. Click `+` → `npm`
3. **Name**: `React Frontend`
4. **Package.json**: `/path/to/your/project/app/frontend/package.json`
5. **Command**: `start`
6. **Working directory**: `/path/to/your/project/app/frontend`
7. Click `OK`

### 7. Frontend Setup

Navigate to frontend directory and install dependencies:
```bash
cd app/frontend
npm install
```

## Running the Application

### Method 1: Using PyCharm Run Configurations
1. Start the backend: Click the play button next to "FastAPI Backend"
2. Start the frontend: Click the play button next to "React Frontend"

### Method 2: Using Terminal
Open two terminals in PyCharm:

**Terminal 1 (Backend):**
```bash
python main.py
```

**Terminal 2 (Frontend):**
```bash
cd app/frontend
npm start
```

## Access URLs
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/docs

## Debugging Setup

### Backend Debugging
1. Set breakpoints in your Python code
2. Right-click the "FastAPI Backend" configuration
3. Select "Debug 'FastAPI Backend'"

### Frontend Debugging
1. Install browser extension for React Developer Tools
2. Use browser developer tools for JavaScript debugging
3. PyCharm Professional has built-in JavaScript debugging support

## Database Management in PyCharm

### Database Tool Window (PyCharm Professional)
1. `View` → `Tool Windows` → `Database`
2. Click `+` → `Data Source` → `PostgreSQL`
3. Enter your database connection details
4. Test connection and apply

### Alternative: DB Browser
Install a database browser like DBeaver or pgAdmin for database management.

## Project Structure Understanding

```
job-application-management/
├── main.py                 # FastAPI application entry point
├── database.py            # Database configuration
├── models.py              # SQLAlchemy models
├── schemas.py             # Pydantic schemas
├── auth.py                # Authentication utilities
├── routers/               # API route handlers
│   ├── auth.py
│   ├── applications.py
│   └── resumes.py
├── app/
│   ├── frontend/          # React application
│   │   ├── src/
│   │   ├── package.json
│   │   └── ...
│   └── backend/           # Alternative backend structure
├── tests/                 # Test files
└── requirements.txt       # Python dependencies
```

## Tips for PyCharm Development

1. **Code Completion**: PyCharm provides excellent autocomplete for FastAPI and SQLAlchemy
2. **Type Hints**: Use type hints for better code assistance
3. **Refactoring**: Use PyCharm's refactoring tools safely
4. **Version Control**: Integrate with Git through PyCharm's VCS tools
5. **Testing**: Use PyCharm's test runner for pytest tests

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Check if PostgreSQL is running
   - Verify DATABASE_URL in environment variables
   - Ensure database and user exist

2. **Frontend Proxy Errors**:
   - Make sure backend is running on port 5000
   - Check `package.json` proxy configuration

3. **Import Errors**:
   - Verify virtual environment is activated
   - Check if all dependencies are installed
   - Restart PyCharm if needed

4. **Port Already in Use**:
   - Kill existing processes: `lsof -ti:5000 | xargs kill -9`
   - Or change ports in configuration

## Production Deployment

For production deployment, refer to the Docker setup files included in the project or use cloud platforms like Heroku, AWS, or DigitalOcean.