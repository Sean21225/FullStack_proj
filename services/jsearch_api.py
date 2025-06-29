"""
JSearch API service for LinkedIn job scraping
Provides job search and company information from LinkedIn, Indeed, Glassdoor, and other job sites
"""
import requests
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class JSearchService:
    """JSearch API service for job data from multiple job sites including LinkedIn"""
    
    def __init__(self):
        self.api_key = os.getenv("JSEARCH_API_KEY", "859eaed2b7msh4e410a5587eb407p1a6b0fjsncc33fe16fc8f")
        self.base_url = "https://jsearch.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        
    def search_jobs(self, query: str, location: Optional[str] = None, 
                   employment_types: Optional[str] = "FULLTIME", 
                   num_pages: int = 1, 
                   date_posted: Optional[str] = "all") -> List[Dict[str, Any]]:
        """
        Search for jobs using JSearch API
        
        Args:
            query: Job search query (e.g., "software engineer", "data scientist")
            location: Location filter (e.g., "New York, NY", "Remote")
            employment_types: Employment types (FULLTIME, PARTTIME, INTERN, CONTRACTOR)
            num_pages: Number of pages to fetch (each page has ~10 jobs)
            date_posted: Date filter (all, today, 3days, week, month)
            
        Returns:
            List of job dictionaries with standardized format
        """
        try:
            url = f"{self.base_url}/search"
            
            params = {
                "query": query,
                "page": "1",
                "num_pages": str(num_pages),
                "date_posted": date_posted,
                "employment_types": employment_types
            }
            
            if location:
                params["location"] = location
                
            logger.info(f"Searching jobs with query: {query}, location: {location}")
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get("status") == "OK":
                logger.error(f"JSearch API error: {data.get('request_info', {}).get('message', 'Unknown error')}")
                return []
                
            jobs = data.get("data", [])
            
            # Transform to standardized format
            standardized_jobs = []
            for job in jobs:
                standardized_job = {
                    "title": job.get("job_title", ""),
                    "company": job.get("employer_name", ""),
                    "location": job.get("job_city", ""),
                    "description": job.get("job_description", ""),
                    "url": job.get("job_apply_link", ""),
                    "posted_date": job.get("job_posted_at_datetime_utc", ""),
                    "employment_type": job.get("job_employment_type", ""),
                    "salary_min": job.get("job_min_salary"),
                    "salary_max": job.get("job_max_salary"),
                    "currency": job.get("job_salary_currency"),
                    "is_remote": job.get("job_is_remote", False),
                    "job_id": job.get("job_id", ""),
                    "source": "jsearch"
                }
                standardized_jobs.append(standardized_job)
                
            logger.info(f"Successfully retrieved {len(standardized_jobs)} jobs")
            return standardized_jobs
            
        except requests.exceptions.RequestException as e:
            logger.error(f"JSearch API request error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"JSearch API error: {str(e)}")
            return []
    
    def get_job_details(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific job
        
        Args:
            job_id: Job ID from search results
            
        Returns:
            Detailed job information or None if not found
        """
        try:
            url = f"{self.base_url}/job-details"
            params = {"job_id": job_id}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") == "OK" and data.get("data"):
                job_data = data["data"][0]
                return {
                    "title": job_data.get("job_title", ""),
                    "company": job_data.get("employer_name", ""),
                    "location": job_data.get("job_city", ""),
                    "description": job_data.get("job_description", ""),
                    "qualifications": job_data.get("job_qualifications", ""),
                    "responsibilities": job_data.get("job_responsibilities", ""),
                    "benefits": job_data.get("job_benefits", ""),
                    "url": job_data.get("job_apply_link", ""),
                    "posted_date": job_data.get("job_posted_at_datetime_utc", ""),
                    "employment_type": job_data.get("job_employment_type", ""),
                    "salary_min": job_data.get("job_min_salary"),
                    "salary_max": job_data.get("job_max_salary"),
                    "currency": job_data.get("job_salary_currency"),
                    "is_remote": job_data.get("job_is_remote", False),
                    "source": "jsearch"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"JSearch job details error: {str(e)}")
            return None
    
    def search_companies(self, company_name: str) -> List[Dict[str, Any]]:
        """
        Search for company information
        Note: JSearch primarily focuses on jobs, so this searches for jobs by company
        
        Args:
            company_name: Company name to search for
            
        Returns:
            List of company information from job postings
        """
        try:
            # Search for jobs from the specific company
            jobs = self.search_jobs(query=f"company:{company_name}", num_pages=1)
            
            if not jobs:
                return []
            
            # Extract unique company information
            companies = {}
            for job in jobs:
                company = job.get("company", "")
                if company and company.lower() == company_name.lower():
                    if company not in companies:
                        companies[company] = {
                            "name": company,
                            "locations": set(),
                            "job_count": 0,
                            "job_titles": set(),
                            "source": "jsearch"
                        }
                    
                    companies[company]["locations"].add(job.get("location", ""))
                    companies[company]["job_count"] += 1
                    companies[company]["job_titles"].add(job.get("title", ""))
            
            # Convert sets to lists for JSON serialization
            result = []
            for company_data in companies.values():
                company_data["locations"] = list(company_data["locations"])
                company_data["job_titles"] = list(company_data["job_titles"])
                result.append(company_data)
            
            return result
            
        except Exception as e:
            logger.error(f"JSearch company search error: {str(e)}")
            return []
    
    def get_trending_jobs(self, location: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get trending/popular job titles
        
        Args:
            location: Optional location filter
            
        Returns:
            List of trending jobs
        """
        try:
            # Search for popular tech jobs as trending
            trending_queries = [
                "software engineer", "data scientist", "product manager", 
                "frontend developer", "backend developer", "devops engineer"
            ]
            
            all_jobs = []
            for query in trending_queries[:3]:  # Limit to avoid rate limits
                jobs = self.search_jobs(query=query, location=location, num_pages=1)
                all_jobs.extend(jobs[:2])  # Take top 2 from each category
            
            return all_jobs
            
        except Exception as e:
            logger.error(f"JSearch trending jobs error: {str(e)}")
            return []

# Global instance
jsearch_service = JSearchService()