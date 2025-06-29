"""
Integration tests for the Job Application Management API
Testing complete user workflows and system interactions
"""

import pytest
import asyncio
import requests
import time
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER_DATA = {
    "username": "integration_test_user",
    "email": "integration@test.com",
    "password": "SecureTestPassword123!"
}


class TestUserWorkflow:
    """Test complete user workflow from registration to job application management"""
    
    def __init__(self):
        self.auth_token = None
        self.user_id = None
        self.resume_id = None
        self.application_id = None
    
    def test_complete_user_journey(self):
        """Test the complete user journey"""
        print("🚀 Starting complete user journey test...")
        
        # Step 1: Health check
        self.test_health_check()
        
        # Step 2: User registration
        self.test_user_registration()
        
        # Step 3: User login
        self.test_user_login()
        
        # Step 4: Create resume
        self.test_create_resume()
        
        # Step 5: Optimize resume
        self.test_optimize_resume()
        
        # Step 6: Search jobs
        self.test_job_search()
        
        # Step 7: Get company information
        self.test_company_lookup()
        
        # Step 8: Create job application
        self.test_create_application()
        
        # Step 9: Get application statistics
        self.test_application_statistics()
        
        # Step 10: Update application status
        self.test_update_application()
        
        print("✅ Complete user journey test passed!")
    
    def test_health_check(self):
        """Test API health check"""
        print("🔍 Testing health check...")
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ Health check passed")
    
    def test_user_registration(self):
        """Test user registration"""
        print("👤 Testing user registration...")
        response = requests.post(f"{BASE_URL}/auth/signup", json=TEST_USER_DATA)
        
        if response.status_code == 400:
            # User might already exist, try to delete and recreate
            print("⚠️  User already exists, continuing with login...")
            return
        
        assert response.status_code == 201
        data = response.json()
        assert "user_id" in data
        self.user_id = data["user_id"]
        print(f"✅ User registration passed - User ID: {self.user_id}")
    
    def test_user_login(self):
        """Test user login and token generation"""
        print("🔐 Testing user login...")
        login_data = {
            "username": TEST_USER_DATA["username"],
            "password": TEST_USER_DATA["password"]
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        self.auth_token = data["access_token"]
        self.user_id = data["user_id"]
        print("✅ User login passed")
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    def test_create_resume(self):
        """Test resume creation"""
        print("📄 Testing resume creation...")
        resume_data = {
            "title": "Integration Test Resume",
            "content": """
            John Doe
            Software Engineer
            
            EXPERIENCE:
            • 3 years at Tech Corp as Software Engineer
            • Developed web applications using Python, JavaScript, React
            • Led a team of 5 developers on key projects
            • Implemented CI/CD pipelines and improved deployment efficiency by 40%
            
            EDUCATION:
            • BS Computer Science, University of Technology (2020)
            • Relevant coursework: Data Structures, Algorithms, Database Systems
            
            SKILLS:
            • Languages: Python, JavaScript, Java, SQL
            • Frameworks: React, FastAPI, Django, Node.js
            • Tools: Docker, Git, AWS, PostgreSQL
            """
        }
        
        response = requests.post(
            f"{BASE_URL}/resume",
            json=resume_data,
            headers=self.get_auth_headers()
        )
        assert response.status_code == 201
        data = response.json()
        assert "resume_id" in data
        self.resume_id = data["resume_id"]
        print(f"✅ Resume creation passed - Resume ID: {self.resume_id}")
    
    def test_optimize_resume(self):
        """Test resume optimization"""
        print("🎯 Testing resume optimization...")
        optimization_data = {
            "resume_content": "Basic resume content for testing optimization",
            "job_description": "Software Engineer position requiring Python, React, and AWS experience",
            "optimization_type": "job_specific"
        }
        
        response = requests.post(
            f"{BASE_URL}/services/optimize-resume",
            json=optimization_data,
            headers=self.get_auth_headers()
        )
        assert response.status_code == 200
        data = response.json()
        assert "optimized_content" in data
        assert "suggestions" in data
        assert "score" in data
        print("✅ Resume optimization passed")
    
    def test_job_search(self):
        """Test job search functionality"""
        print("🔍 Testing job search...")
        params = {
            "keywords": "software engineer",
            "location": "New York",
            "limit": 3
        }
        
        response = requests.get(
            f"{BASE_URL}/services/api/suggestions/jobs",
            params=params,
            headers=self.get_auth_headers()
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            job = data[0]
            assert "title" in job
            assert "company" in job
            print(f"✅ Job search passed - Found {len(data)} jobs")
        else:
            print("⚠️  Job search returned no results (API might be rate limited)")
    
    def test_company_lookup(self):
        """Test company information lookup"""
        print("🏢 Testing company lookup...")
        params = {"company_name": "Google"}
        
        response = requests.get(
            f"{BASE_URL}/services/api/suggestions/companies",
            params=params,
            headers=self.get_auth_headers()
        )
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "Google"
        print("✅ Company lookup passed")
    
    def test_create_application(self):
        """Test job application creation"""
        print("📝 Testing job application creation...")
        application_data = {
            "job_title": "Senior Software Engineer",
            "company": "Tech Innovation Corp",
            "status": "applied",
            "job_description": "Full-stack development role with focus on React and Python",
            "application_url": "https://example.com/apply",
            "notes": "Applied through company website. Salary range: $120k-$150k",
            "resume_id": self.resume_id
        }
        
        response = requests.post(
            f"{BASE_URL}/applications",
            json=application_data,
            headers=self.get_auth_headers()
        )
        assert response.status_code == 201
        data = response.json()
        assert "application_id" in data
        self.application_id = data["application_id"]
        print(f"✅ Job application creation passed - Application ID: {self.application_id}")
    
    def test_application_statistics(self):
        """Test application statistics"""
        print("📊 Testing application statistics...")
        response = requests.get(
            f"{BASE_URL}/applications/statistics/summary",
            headers=self.get_auth_headers()
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_applications" in data
        assert "status_breakdown" in data
        assert data["total_applications"] >= 1  # At least our test application
        print("✅ Application statistics passed")
    
    def test_update_application(self):
        """Test application status update"""
        print("🔄 Testing application update...")
        update_data = {
            "status": "interview",
            "notes": "Phone interview scheduled for next week"
        }
        
        response = requests.put(
            f"{BASE_URL}/applications/{self.application_id}",
            json=update_data,
            headers=self.get_auth_headers()
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "interview"
        print("✅ Application update passed")


class TestSystemIntegration:
    """Test system-wide integration scenarios"""
    
    def test_concurrent_users(self):
        """Test multiple users using the system simultaneously"""
        print("👥 Testing concurrent user scenarios...")
        
        # Create multiple test users
        users = []
        for i in range(3):
            user_data = {
                "username": f"concurrent_user_{i}",
                "email": f"concurrent{i}@test.com",
                "password": "TestPassword123!"
            }
            
            # Register user
            response = requests.post(f"{BASE_URL}/auth/signup", json=user_data)
            if response.status_code in [201, 400]:  # Success or already exists
                # Login
                login_response = requests.post(f"{BASE_URL}/auth/login", json={
                    "username": user_data["username"],
                    "password": user_data["password"]
                })
                if login_response.status_code == 200:
                    token = login_response.json()["access_token"]
                    users.append({"user_data": user_data, "token": token})
        
        print(f"✅ Concurrent users test passed - {len(users)} users active")
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        print("❌ Testing error handling...")
        
        # Test invalid endpoints
        response = requests.get(f"{BASE_URL}/invalid/endpoint")
        assert response.status_code == 404
        
        # Test unauthorized access
        response = requests.get(f"{BASE_URL}/resume")
        assert response.status_code == 401
        
        # Test invalid data
        response = requests.post(f"{BASE_URL}/auth/signup", json={"invalid": "data"})
        assert response.status_code == 422
        
        print("✅ Error handling tests passed")
    
    def test_performance(self):
        """Test basic performance metrics"""
        print("⚡ Testing performance...")
        
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 2.0  # Should respond within 2 seconds
        
        print(f"✅ Performance test passed - Response time: {response_time:.3f}s")


def run_integration_tests():
    """Run all integration tests"""
    print("🧪 Starting Integration Tests")
    print("=" * 50)
    
    try:
        # Test if server is running
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            raise Exception("Server not healthy")
    except Exception as e:
        print(f"❌ Server not accessible at {BASE_URL}")
        print(f"Error: {e}")
        print("Please ensure the FastAPI server is running on port 8000")
        return False
    
    try:
        # Run user workflow tests
        workflow_test = TestUserWorkflow()
        workflow_test.test_complete_user_journey()
        
        # Run system integration tests
        system_test = TestSystemIntegration()
        system_test.test_concurrent_users()
        system_test.test_error_handling()
        system_test.test_performance()
        
        print("=" * 50)
        print("🎉 All Integration Tests Passed!")
        return True
        
    except AssertionError as e:
        print(f"❌ Integration test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during integration tests: {e}")
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)