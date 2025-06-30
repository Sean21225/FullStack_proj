"""
Adzuna API service for worldwide job search
Provides global job coverage with excellent free tier
1000 calls/month free, covers major job sites worldwide
"""
import requests
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class AdzunaJobsService:
    """Adzuna API service - worldwide job search with generous free tier"""
    
    def __init__(self):
        self.app_id = os.getenv("ADZUNA_APP_ID", "02cdd573")
        self.app_key = os.getenv("ADZUNA_APP_KEY", "e069475e9bb8a57ca1f17f94a4da6199")
        self.base_url = "https://api.adzuna.com/v1/api"
        # Adzuna has a generous free tier with 1000 calls/month
    
    def search_jobs(self, query: str, location: Optional[str] = None, 
                   employment_types: Optional[str] = "FULLTIME", 
                   experience_level: Optional[str] = None,
                   limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for jobs using Adzuna API
        
        Args:
            query: Job search query (e.g., "software engineer", "data scientist")
            location: Location filter (e.g., "Tel Aviv, Israel", "Washington, DC")
            employment_types: Employment types filter
            experience_level: Experience level filter
            limit: Maximum number of results to return
            
        Returns:
            List of job dictionaries with standardized format
        """
        try:
            # Map location to Adzuna country codes (only supported countries)
            country_mapping = {
                "washington": "us",
                "united states": "us",
                "usa": "us",
                "new york": "us",
                "california": "us",
                "texas": "us",
                "florida": "us",
                "london": "gb",
                "uk": "gb",
                "united kingdom": "gb",
                "manchester": "gb",
                "birmingham": "gb",
                "berlin": "de",
                "germany": "de",
                "munich": "de",
                "hamburg": "de",
                "paris": "fr",
                "france": "fr",
                "lyon": "fr",
                "marseille": "fr",
                "amsterdam": "nl",
                "netherlands": "nl",
                "rotterdam": "nl",
                "toronto": "ca",
                "canada": "ca",
                "vancouver": "ca",
                "montreal": "ca",
                "sydney": "au",
                "australia": "au",
                "melbourne": "au",
                "brisbane": "au"
            }
            
            # Check if location is supported
            country_code = None
            if location:
                location_lower = location.lower()
                for key, code in country_mapping.items():
                    if key in location_lower:
                        country_code = code
                        break
            
            # If location not supported or no location specified, default to US
            if not country_code:
                if location:
                    location_check = location.lower()
                    if "tel aviv" in location_check or "israel" in location_check:
                        logger.warning(f"Location '{location}' not supported by Adzuna API")
                        return []
                country_code = "us"
            
            # Build search query with experience level
            search_query = query
            if experience_level:
                level_terms = {
                    "internship": "intern internship",
                    "entry_level": "entry level junior",
                    "associate": "associate",
                    "mid_senior": "senior mid level",
                    "director": "director manager",
                    "executive": "executive VP president"
                }
                if experience_level in level_terms:
                    search_query = f"{query} {level_terms[experience_level]}"
            
            # Adzuna API endpoint
            url = f"{self.base_url}/jobs/{country_code}/search/1"
            
            params = {
                "app_id": self.app_id,
                "app_key": self.app_key,
                "what": search_query,
                "results_per_page": min(limit, 50),
                "sort_by": "relevance"
            }
            
            # Add location filter if specified
            if location:
                params["where"] = location
            
            logger.info(f"Searching Adzuna for '{search_query}' in '{location}' (country: {country_code})")
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if "results" not in data:
                logger.warning(f"No results field in Adzuna response for '{search_query}' in '{location}'")
                return []
            
            jobs_results = data.get("results", [])
            
            if not jobs_results:
                logger.warning(f"No jobs found for query '{search_query}' in '{location}'")
                return []
            
            # Transform to standardized format
            standardized_jobs = []
            for job in jobs_results[:limit]:
                # Extract salary information
                salary_min = job.get("salary_min")
                salary_max = job.get("salary_max")
                currency = "USD" if country_code == "us" else "EUR"
                
                # Parse posted date
                posted_date = ""
                if job.get("created"):
                    try:
                        # Adzuna provides ISO format dates
                        posted_date = job["created"][:10]  # Get just the date part
                    except:
                        posted_date = ""
                
                # Extract location information
                job_location = job.get("location", {})
                location_display = ""
                if isinstance(job_location, dict):
                    display_name = job_location.get("display_name", "")
                    area = job_location.get("area", [""])[0] if job_location.get("area") else ""
                    location_display = display_name or area
                else:
                    location_display = str(job_location)
                
                # Check if it's a remote job
                job_title = job.get("title", "").lower()
                job_desc = job.get("description", "").lower()
                is_remote = (
                    "remote" in job_title or
                    "remote" in job_desc or
                    "work from home" in job_desc or
                    "wfh" in job_desc
                )
                
                # Get apply URL
                apply_url = job.get("redirect_url", "")
                
                standardized_job = {
                    "title": job.get("title", ""),
                    "company": job.get("company", {}).get("display_name", "") if job.get("company") else "",
                    "location": location_display,
                    "description": job.get("description", "")[:500] + "...",  # Truncate description
                    "url": apply_url,
                    "posted_date": posted_date,
                    "employment_type": job.get("contract_type", "FULLTIME"),
                    "salary_min": salary_min,
                    "salary_max": salary_max,
                    "currency": currency,
                    "is_remote": is_remote,
                    "job_id": job.get("id", ""),
                    "source": "adzuna"
                }
                standardized_jobs.append(standardized_job)
            
            logger.info(f"Successfully retrieved {len(standardized_jobs)} jobs from Adzuna")
            return standardized_jobs
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Adzuna API request error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Adzuna API error: {str(e)}")
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
            # Search for jobs from the specific company
            jobs = self.search_jobs(query=f"{company_name}", limit=20)
            
            if not jobs:
                return []
            
            # Extract company information from jobs
            company_locations = set()
            for job in jobs:
                if job.get("location"):
                    company_locations.add(job["location"])
            
            return [{
                "name": company_name,
                "industry": "Technology",  # Default assumption
                "size": f"~{len(jobs)} current job openings",
                "description": f"Company with {len(jobs)} active job postings across multiple job sites",
                "website": None,
                "headquarters": ", ".join(list(company_locations)[:3]) if company_locations else None,
                "job_count": len(jobs)
            }]
            
        except Exception as e:
            logger.error(f"Adzuna company search error: {str(e)}")
            return []

# Create singleton instance
adzuna_jobs_service = AdzunaJobsService()