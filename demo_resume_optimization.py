#!/usr/bin/env python3
"""
Demonstration of Free Resume Optimization System
Shows all features working without any API costs
"""

import requests
import json

# API configuration
BASE_URL = "http://localhost:5000"
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsInVzZXJfaWQiOjMsImV4cCI6MTc1MTE5MjU5OH0.U8JFU7DcZ4DUchaVlHLPIX5xMKQZDMAxNQlSry3oZ0s"

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def test_resume_optimization():
    """Test the free resume optimization feature"""
    print_section("TESTING FREE RESUME OPTIMIZATION")
    
    # Test data - basic resume that needs improvement
    test_resume = """Michael Chen
Software Developer

Experience:
- Worked at StartupXYZ for 18 months
- Responsible for building features
- Used React and Node.js
- Fixed bugs and issues

Education:
- Computer Science Degree
- State University

Skills:
- JavaScript
- Problem solving"""

    job_description = """Senior Frontend Engineer
We're seeking a Senior Frontend Engineer with 3+ years of experience in React, TypeScript, and modern web technologies. You'll lead development of user-facing features, mentor junior developers, and work closely with design teams. 

Requirements:
- 3+ years React experience
- TypeScript proficiency
- Experience with testing frameworks (Jest, Cypress)
- Knowledge of CI/CD pipelines
- Agile/Scrum methodology experience
- Strong communication and leadership skills"""

    optimization_request = {
        "resume_content": test_resume,
        "job_description": job_description,
        "optimization_type": "job_specific"
    }
    
    print("Original Resume:")
    print("-" * 40)
    print(test_resume)
    print("\nJob Description:")
    print("-" * 40)
    print(job_description[:200] + "...")
    
    # Call optimization service
    try:
        response = requests.post(
            f"{BASE_URL}/services/optimize-resume",
            headers=headers,
            json=optimization_request
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n" + "="*60)
            print("OPTIMIZATION RESULTS")
            print("="*60)
            
            print(f"\nResume Score: {result['score']:.1%}")
            
            print("\nOptimized Content:")
            print("-" * 40)
            print(result['optimized_content'])
            
            print("\nAI Suggestions:")
            print("-" * 40)
            for i, suggestion in enumerate(result['suggestions'], 1):
                print(f"{i}. {suggestion}")
                
            return True
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Request failed: {e}")
        return False

def test_resume_analysis():
    """Test the resume analysis feature"""
    print_section("TESTING RESUME ANALYSIS")
    
    try:
        response = requests.get(
            f"{BASE_URL}/services/api/optimizer/analyze/4",
            headers=headers
        )
        
        if response.status_code == 200:
            analysis = response.json()
            
            print(f"Resume Score: {analysis['score']:.1%}")
            print(f"Word Count: {analysis['word_count']}")
            print(f"ATS Friendly: {'Yes' if analysis['ats_friendly'] else 'No'}")
            print(f"Readability: {analysis['readability']}")
            
            print("\nStrengths:")
            for strength in analysis['strengths']:
                print(f"  ✓ {strength}")
                
            print("\nAreas for Improvement:")
            for weakness in analysis['weaknesses']:
                print(f"  ⚠ {weakness}")
                
            print("\nRecommendations:")
            for i, suggestion in enumerate(analysis['suggestions'][:5], 1):
                print(f"  {i}. {suggestion}")
                
            return True
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Request failed: {e}")
        return False

def test_different_optimization_types():
    """Test different optimization types"""
    print_section("TESTING OPTIMIZATION TYPES")
    
    base_resume = """Jane Smith
Marketing Manager

Experience:
- Managed social media accounts
- Created content for campaigns
- Worked with design team

Education:
- MBA Marketing
- Business University

Skills:
- Social media
- Content creation"""

    optimization_types = [
        ("general", "General optimization for any job"),
        ("job_specific", "Tailored for specific job requirements"),
        ("ats_optimized", "Optimized for Applicant Tracking Systems")
    ]
    
    for opt_type, description in optimization_types:
        print(f"\nTesting: {description}")
        print("-" * 40)
        
        request_data = {
            "resume_content": base_resume,
            "job_description": "Digital Marketing Manager position requiring social media expertise, content strategy, and analytics skills.",
            "optimization_type": opt_type
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/services/optimize-resume",
                headers=headers,
                json=request_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Score: {result['score']:.1%}")
                print(f"Suggestions: {len(result['suggestions'])} recommendations")
                print("Top suggestion:", result['suggestions'][0] if result['suggestions'] else "None")
            else:
                print(f"Error: {response.status_code}")
                
        except Exception as e:
            print(f"Request failed: {e}")

def main():
    """Run all demonstration tests"""
    print("FREE RESUME OPTIMIZATION SYSTEM DEMONSTRATION")
    print("No API costs • No external dependencies • Works offline")
    
    tests = [
        ("Resume Optimization", test_resume_optimization),
        ("Resume Analysis", test_resume_analysis),
        ("Optimization Types", test_different_optimization_types)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"Test {test_name} failed: {e}")
            results.append((test_name, False))
    
    # Summary
    print_section("TEST RESULTS SUMMARY")
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Free resume optimization is fully functional.")
        print("📍 No API costs or external dependencies required")
        print("🚀 Ready for production use")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")

if __name__ == "__main__":
    main()