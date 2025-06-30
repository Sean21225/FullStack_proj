"""
Arbeitnow Free Job Board API service
Provides unlimited free job search from European job boards and remote positions
No API key required - completely free service
"""
import requests
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class ArbeitnowService:
    """Arbeitnow Free Job Board API service - unlimited free job search"""
    
    def __init__(self):
        self.base_url = "https://www.arbeitnow.com/api/job-board-api"
        # No API key required - completely free service
    
    def _normalize_location(self, location: str) -> str:
        """
        Normalize location string for better filtering
        
        Args:
            location: Raw location string from user input
            
        Returns:
            Normalized location string
        """
        if not location:
            return location
            
        location = location.strip().lower()
        
        # Common location mappings
        location_mappings = {
            "tel aviv": "tel aviv",
            "tel-aviv": "tel aviv", 
            "telaviv": "tel aviv",
            "israel": "israel",
            "jerusalem": "jerusalem",
            "haifa": "haifa",
            "new york": "new york",
            "nyc": "new york",
            "sf": "san francisco",
            "san francisco": "san francisco",
            "la": "los angeles",
            "los angeles": "los angeles",
            "london": "london",
            "paris": "paris",
            "berlin": "berlin",
            "munich": "munich",
            "amsterdam": "amsterdam",
            "barcelona": "barcelona",
            "madrid": "madrid",
            "rome": "rome",
            "milan": "milan",
            "vienna": "vienna",
            "zurich": "zurich",
            "stockholm": "stockholm",
            "copenhagen": "copenhagen",
            "oslo": "oslo",
            "dublin": "dublin",
            "tokyo": "tokyo"
        }
        
        return location_mappings.get(location, location)
    
    def _filter_jobs_by_keywords(self, jobs: List[Dict[str, Any]], keywords: str) -> List[Dict[str, Any]]:
        """
        Filter jobs by keyword relevance
        
        Args:
            jobs: List of job dictionaries
            keywords: Search keywords to match against
            
        Returns:
            Filtered list of jobs matching keywords
        """
        if not jobs or not keywords:
            return jobs
        
        # Extract keywords and create search terms
        search_terms = set()
        for term in keywords.lower().split():
            # Remove common words that don't help with job matching
            if term not in ['and', 'or', 'the', 'a', 'an', 'in', 'at', 'of', 'for', 'with']:
                search_terms.add(term)
        
        # Add variations for common tech terms
        tech_variations = {
            'js': ['javascript', 'js'],
            'javascript': ['javascript', 'js'],
            'python': ['python', 'django', 'flask'],
            'react': ['react', 'reactjs', 'react.js'],
            'vue': ['vue', 'vuejs', 'vue.js'],
            'angular': ['angular', 'angularjs'],
            'node': ['node', 'nodejs', 'node.js'],
            'ai': ['ai', 'artificial intelligence', 'machine learning', 'ml'],
            'ml': ['machine learning', 'ml', 'ai'],
            'data': ['data', 'analytics', 'scientist'],
            'software': ['software', 'engineer', 'developer', 'programming'],
            'frontend': ['frontend', 'front-end', 'ui', 'user interface'],
            'backend': ['backend', 'back-end', 'api', 'server'],
            'fullstack': ['fullstack', 'full-stack', 'full stack'],
            'devops': ['devops', 'dev ops', 'infrastructure', 'cloud'],
            'mobile': ['mobile', 'ios', 'android', 'react native', 'flutter']
        }
        
        # Expand search terms with variations
        expanded_terms = set(search_terms)
        for term in search_terms:
            if term in tech_variations:
                expanded_terms.update(tech_variations[term])
        
        filtered_jobs = []
        for job in jobs:
            # Create searchable text from job fields
            tags_text = ""
            if job.get("tags"):
                if isinstance(job.get("tags"), list):
                    tags_text = " ".join(job.get("tags", []))
                else:
                    tags_text = str(job.get("tags", ""))
            
            job_types_text = ""
            if job.get("job_types"):
                if isinstance(job.get("job_types"), list):
                    job_types_text = " ".join(job.get("job_types", []))
                else:
                    job_types_text = str(job.get("job_types", ""))
            
            searchable_text = " ".join([
                (job.get("title") or "").lower(),
                (job.get("description") or "").lower(),
                tags_text.lower(),
                job_types_text.lower()
            ])
            
            # Check if any search terms match
            matches = 0
            for term in expanded_terms:
                if term in searchable_text:
                    matches += 1
            
            # Include job if it has reasonable keyword matches
            if matches > 0 or len(search_terms) == 0:
                job['relevance_score'] = matches
                filtered_jobs.append(job)
        
        # Sort by relevance score (highest first)
        filtered_jobs.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        logger.info(f"Keyword filtering for '{keywords}': {len(jobs)} -> {len(filtered_jobs)} jobs")
        return filtered_jobs
    
    def _filter_jobs_by_location(self, jobs: List[Dict[str, Any]], location: str) -> List[Dict[str, Any]]:
        """
        Filter jobs by location relevance - strict filtering for specific locations
        
        Args:
            jobs: List of job dictionaries
            location: Location to filter by
            
        Returns:
            Filtered list of jobs matching location
        """
        if not jobs or not location:
            return jobs
        
        normalized_location = self._normalize_location(location)
        location_keywords = [kw.lower() for kw in normalized_location.split()]
        
        filtered_jobs = []
        for job in jobs:
            # Create searchable location text
            job_location = (job.get("location") or "").lower()
            job_city = (job.get("city") or "").lower() 
            job_country = (job.get("country") or "").lower()
            
            # Combine all location fields for searching
            full_location_text = f"{job_location} {job_city} {job_country}".strip()
            
            # Check for remote jobs only if user specifically searches for "remote"
            job_tags = job.get("tags", [])
            if isinstance(job_tags, str):
                job_tags = [job_tags]
            elif not isinstance(job_tags, list):
                job_tags = []
            
            is_remote_job = (job.get("remote", False) or 
                           "remote" in full_location_text or
                           any(tag.lower() in ["remote", "home office", "homeoffice"] 
                               for tag in job_tags if isinstance(tag, str)))
            
            # If user searches for "remote", include remote jobs
            if location.lower() in ["remote", "anywhere", "global"]:
                if is_remote_job:
                    filtered_jobs.append(job)
                continue
            
            # For specific locations, use strict matching
            location_match = False
            
            # Check for exact city/location matches first
            for keyword in location_keywords:
                if len(keyword) > 2:  # Only check meaningful keywords
                    # Exact word match in any location field
                    if (keyword in job_location.split() or 
                        keyword in job_city.split() or
                        keyword in job_country.split()):
                        location_match = True
                        break
                    
                    # Partial match for compound city names (like "tel aviv")
                    if keyword in job_location or keyword in job_city:
                        location_match = True
                        break
            
            # Special handling for common location variations
            if not location_match:
                # Handle specific city mappings
                location_mappings = {
                    "tel aviv": ["tel aviv", "israel"],
                    "washington": ["washington", "dc", "usa", "united states"],
                    "new york": ["new york", "ny", "nyc", "usa", "united states"],
                    "san francisco": ["san francisco", "sf", "california", "ca", "usa"],
                    "london": ["london", "uk", "united kingdom", "england"],
                    "paris": ["paris", "france"],
                    "berlin": ["berlin", "germany"],
                    "munich": ["munich", "münchen", "germany"],
                    "amsterdam": ["amsterdam", "netherlands"]
                }
                
                search_location = location.lower()
                if search_location in location_mappings:
                    expected_terms = location_mappings[search_location]
                    if any(term in full_location_text for term in expected_terms):
                        location_match = True
            
            # Include job if location matches
            if location_match:
                filtered_jobs.append(job)
        
        # If no location matches found, just return empty list - we'll use Google Jobs API as fallback
        if len(filtered_jobs) == 0:
            logger.info(f"No location matches for '{location}' in Arbeitnow database")
        
        logger.info(f"Location filtering for '{location}': {len(jobs)} -> {len(filtered_jobs)} jobs")
        return filtered_jobs
    
    def search_jobs(self, query: str, location: Optional[str] = None, 
                   employment_types: Optional[str] = "FULLTIME", 
                   experience_level: Optional[str] = None,
                   limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for jobs using Arbeitnow Free API
        
        Args:
            query: Job search query (e.g., "software engineer", "data scientist")
            location: Location filter (e.g., "Berlin", "Remote")
            employment_types: Employment types (not directly supported by Arbeitnow)
            experience_level: Experience level filter (junior, senior, etc.)
            limit: Maximum number of results to return
            
        Returns:
            List of job dictionaries with standardized format
        """
        try:
            # Base API call - gets all jobs (free, unlimited)
            url = self.base_url
            
            # Add remote filter if no location specified or if location suggests remote work
            params = {}
            if not location or location.lower() in ['remote', 'anywhere', 'global']:
                params['remote'] = 'true'
            
            logger.info(f"Searching Arbeitnow jobs with query: {query}, location: {location}")
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Arbeitnow returns data in 'data' field
            jobs = data.get("data", [])
            
            if not jobs:
                logger.warning("No jobs returned from Arbeitnow API")
                return []
            
            logger.info(f"Retrieved {len(jobs)} total jobs from Arbeitnow")
            
            # Filter by keywords first
            if query and query.strip():
                jobs = self._filter_jobs_by_keywords(jobs, query)
            
            # Filter by location if specified
            if location and location.lower() not in ['remote', 'anywhere', 'global']:
                jobs = self._filter_jobs_by_location(jobs, location)
            
            # Filter by experience level if specified
            if experience_level:
                level_keywords = {
                    "internship": ["intern", "internship", "trainee"],
                    "entry_level": ["junior", "entry", "graduate", "entry-level"],
                    "associate": ["associate", "mid", "intermediate"],
                    "mid_senior": ["senior", "lead", "principal"],
                    "director": ["director", "manager", "head"],
                    "executive": ["executive", "ceo", "cto", "vp", "vice president"]
                }
                
                if experience_level in level_keywords:
                    keywords = level_keywords[experience_level]
                    experience_filtered = []
                    
                    for job in jobs:
                        job_text = " ".join([
                            (job.get("title") or "").lower(),
                            (job.get("description") or "").lower()
                        ])
                        
                        if any(keyword in job_text for keyword in keywords):
                            experience_filtered.append(job)
                    
                    if experience_filtered:
                        jobs = experience_filtered
                        logger.info(f"Experience level filtering for '{experience_level}': {len(jobs)} jobs")
            
            # Transform to standardized format
            standardized_jobs = []
            for job in jobs[:limit]:  # Apply limit
                # Parse posted date
                posted_date = ""
                if job.get("created_at"):
                    try:
                        created_at = job["created_at"]
                        # Handle different date formats from Arbeitnow
                        if isinstance(created_at, (int, float)):
                            # If it's a timestamp, convert it
                            dt = datetime.fromtimestamp(created_at)
                            posted_date = dt.strftime("%Y-%m-%d")
                        elif isinstance(created_at, str):
                            # If it's a string, try to parse as ISO format
                            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            posted_date = dt.strftime("%Y-%m-%d")
                        else:
                            posted_date = str(created_at)
                    except Exception as e:
                        # Fallback to empty string if parsing fails
                        posted_date = ""
                
                # Extract location information
                location_parts = []
                if job.get("location"):
                    location_parts.append(job["location"])
                
                # Build job URL
                job_url = job.get("url", "")
                if not job_url and job.get("slug"):
                    job_url = f"https://www.arbeitnow.com/jobs/{job['slug']}"
                
                standardized_job = {
                    "title": job.get("title", ""),
                    "company": job.get("company_name", ""),
                    "location": ", ".join(location_parts) if location_parts else "Remote",
                    "description": job.get("description", ""),
                    "url": job_url,
                    "posted_date": posted_date,
                    "employment_type": "FULLTIME",  # Most Arbeitnow jobs are full-time
                    "salary_min": None,
                    "salary_max": None,
                    "currency": None,
                    "is_remote": job.get("remote", False),
                    "job_id": job.get("slug", ""),
                    "tags": job.get("tags", []),
                    "source": "arbeitnow"
                }
                standardized_jobs.append(standardized_job)
            
            logger.info(f"Successfully processed {len(standardized_jobs)} jobs from Arbeitnow")
            return standardized_jobs
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Arbeitnow API request error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Arbeitnow API error: {str(e)}")
            return []
    
    def search_companies(self, company_name: str) -> List[Dict[str, Any]]:
        """
        Search for company information by searching jobs from that company
        
        Args:
            company_name: Company name to search for
            
        Returns:
            List of companies with basic information
        """
        try:
            # Search all jobs and filter by company
            response = requests.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            jobs = data.get("data", [])
            
            # Find jobs from the specified company
            company_jobs = []
            company_name_lower = company_name.lower()
            
            for job in jobs:
                job_company = (job.get("company_name") or "").lower()
                if company_name_lower in job_company or job_company in company_name_lower:
                    company_jobs.append(job)
            
            if not company_jobs:
                return []
            
            # Extract company information from jobs
            companies = {}
            for job in company_jobs:
                company_key = job.get("company_name", "")
                if company_key not in companies:
                    companies[company_key] = {
                        "name": job.get("company_name", ""),
                        "industry": "Technology",  # Most Arbeitnow jobs are tech
                        "size": None,
                        "description": f"Company posting jobs on Arbeitnow job board. Currently has {len([j for j in company_jobs if j.get('company_name') == company_key])} open positions.",
                        "website": None,
                        "headquarters": job.get("location", ""),
                        "job_count": len([j for j in company_jobs if j.get('company_name') == company_key])
                    }
            
            return list(companies.values())
            
        except Exception as e:
            logger.error(f"Arbeitnow company search error: {str(e)}")
            return []

# Create singleton instance
arbeitnow_service = ArbeitnowService()