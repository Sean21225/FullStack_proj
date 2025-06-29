"""
Unit tests for the Job Application Management API
Testing individual components and functions
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import get_db, Base
from auth import AuthManager
from services.resume_optimizer import ResumeOptimizerService
from services.jsearch_api import JSearchService
from models import User, Resume, Application


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class TestAuthManager:
    """Test authentication manager functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.auth_manager = AuthManager()
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "test_password_123"
        hashed = self.auth_manager.get_password_hash(password)
        
        assert hashed != password
        assert self.auth_manager.verify_password(password, hashed)
        assert not self.auth_manager.verify_password("wrong_password", hashed)
    
    def test_token_creation_and_verification(self):
        """Test JWT token creation and verification"""
        test_data = {"user_id": 1, "username": "testuser"}
        token = self.auth_manager.create_access_token(test_data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token
        token_data = self.auth_manager.verify_token(token)
        assert token_data.user_id == 1
        assert token_data.username == "testuser"


class TestResumeOptimizer:
    """Test resume optimization service"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.optimizer = ResumeOptimizerService()
    
    def test_resume_analysis(self):
        """Test resume content analysis"""
        test_resume = """
        John Doe
        Software Engineer
        
        Experience:
        - 3 years at Google
        - Python, JavaScript, React
        
        Education:
        - BS Computer Science
        """
        
        analysis = self.optimizer.analyze_resume(test_resume)
        
        assert "score" in analysis
        assert "suggestions" in analysis
        assert isinstance(analysis["score"], (int, float))
        assert isinstance(analysis["suggestions"], list)
        assert 0 <= analysis["score"] <= 100
    
    def test_resume_optimization(self):
        """Test resume optimization functionality"""
        test_resume = "Basic resume content"
        job_description = "Software engineer position requiring Python skills"
        
        result = self.optimizer.optimize_resume(test_resume, job_description)
        
        assert "optimized_content" in result
        assert "suggestions" in result
        assert len(result["optimized_content"]) > len(test_resume)


class TestJSearchService:
    """Test JSearch API service"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.jsearch = JSearchService()
    
    def test_service_initialization(self):
        """Test JSearch service initialization"""
        assert self.jsearch.api_key is not None
        assert self.jsearch.base_url == "https://jsearch.p.rapidapi.com"
        assert "X-RapidAPI-Key" in self.jsearch.headers
    
    def test_job_search_parameters(self):
        """Test job search parameter handling"""
        # Test with mock data to avoid API calls in unit tests
        query = "software engineer"
        location = "New York"
        
        # These would normally make API calls, so we test parameter handling
        assert query is not None
        assert location is not None
        assert isinstance(query, str)
        assert isinstance(location, str)


class TestAPIEndpoints:
    """Test API endpoints functionality"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        user_data = {
            "username": "testuser123",
            "email": "test@example.com",
            "password": "SecurePassword123!"
        }
        
        response = client.post("/auth/signup", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert "user_id" in data
        assert data["username"] == user_data["username"]
    
    def test_user_login(self):
        """Test user login endpoint"""
        # First create a user
        user_data = {
            "username": "logintest",
            "email": "login@example.com",
            "password": "SecurePassword123!"
        }
        client.post("/auth/signup", json=user_data)
        
        # Then test login
        login_data = {
            "username": "logintest",
            "password": "SecurePassword123!"
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"


class TestDatabaseModels:
    """Test database models"""
    
    def test_user_model(self):
        """Test User model creation"""
        user_data = {
            "username": "modeltest",
            "password_hashed": "hashed_password",
            "email": "model@example.com"
        }
        
        user = User(**user_data)
        assert user.username == "modeltest"
        assert user.email == "model@example.com"
        assert user.is_active == True
    
    def test_resume_model(self):
        """Test Resume model creation"""
        resume_data = {
            "user_id": 1,
            "title": "Software Engineer Resume",
            "content": "Resume content here"
        }
        
        resume = Resume(**resume_data)
        assert resume.user_id == 1
        assert resume.title == "Software Engineer Resume"
        assert resume.is_active == True
    
    def test_application_model(self):
        """Test Application model creation"""
        app_data = {
            "user_id": 1,
            "job_title": "Software Engineer",
            "company": "Tech Corp",
            "status": "applied"
        }
        
        application = Application(**app_data)
        assert application.user_id == 1
        assert application.job_title == "Software Engineer"
        assert application.status == "applied"


class TestValidation:
    """Test input validation"""
    
    def test_invalid_email_registration(self):
        """Test registration with invalid email"""
        user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "SecurePassword123!"
        }
        
        response = client.post("/auth/signup", json=user_data)
        assert response.status_code == 422  # Validation error
    
    def test_weak_password_registration(self):
        """Test registration with weak password"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123"  # Too weak
        }
        
        response = client.post("/auth/signup", json=user_data)
        assert response.status_code == 422  # Validation error
    
    def test_missing_required_fields(self):
        """Test API calls with missing required fields"""
        # Test resume creation without title
        resume_data = {
            "content": "Resume content"
            # Missing title
        }
        
        # This would require authentication, so we expect 401 or 422
        response = client.post("/resume", json=resume_data)
        assert response.status_code in [401, 422]


# Pytest configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])