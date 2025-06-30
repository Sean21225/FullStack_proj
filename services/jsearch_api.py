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
    
    def _normalize_location(self, location: str) -> str:
        """
        Normalize location string for better API results
        
        Args:
            location: Raw location string from user input
            
        Returns:
            Normalized location string
        """
        if not location:
            return location
            
        location = location.strip()
        
        # Common location mappings for better results
        location_mappings = {
            "tel aviv": "Tel Aviv, Israel",
            "tel-aviv": "Tel Aviv, Israel", 
            "telaviv": "Tel Aviv, Israel",
            "israel": "Israel",
            "jerusalem": "Jerusalem, Israel",
            "haifa": "Haifa, Israel",
            "new york": "New York, NY",
            "nyc": "New York, NY",
            "sf": "San Francisco, CA",
            "san francisco": "San Francisco, CA",
            "la": "Los Angeles, CA",
            "los angeles": "Los Angeles, CA",
            "london": "London, UK",
            "paris": "Paris, France",
            "berlin": "Berlin, Germany",
            "tokyo": "Tokyo, Japan"
        }
        
        location_lower = location.lower()
        return location_mappings.get(location_lower, location)
    
    def _is_us_location(self, location: str) -> bool:
        """
        Check if a location is likely in the US
        
        Args:
            location: Location string to check
            
        Returns:
            True if location appears to be US-based
        """
        if not location:
            return False
            
        location_lower = location.lower()
        us_indicators = [
            ', ny', ', ca', ', tx', ', fl', ', il', ', pa', ', oh', ', ga', ', nc', ', mi',
            'new york', 'california', 'texas', 'florida', 'washington dc', 'chicago',
            'los angeles', 'san francisco', 'boston', 'seattle', 'atlanta', 'miami',
            'united states', 'usa', 'us'
        ]
        
        return any(indicator in location_lower for indicator in us_indicators)
    
    def _filter_jobs_by_location(self, jobs: List[Dict[str, Any]], original_location: str, normalized_location: str) -> List[Dict[str, Any]]:
        """
        Filter jobs by location relevance to improve search accuracy
        
        Args:
            jobs: List of job dictionaries
            original_location: Original location string from user
            normalized_location: Normalized location string
            
        Returns:
            Filtered list of jobs more relevant to the requested location
        """
        if not jobs or not original_location:
            return jobs
        
        # Extract location keywords for matching
        location_keywords = set()
        for loc in [original_location.lower(), normalized_location.lower()]:
            # Split by common delimiters and add individual words
            words = loc.replace(',', ' ').replace('-', ' ').split()
            location_keywords.update(words)
        
        # Remove common words that don't help with location matching
        common_words = {'in', 'the', 'at', 'of', 'and', 'or', 'a', 'an'}
        location_keywords = location_keywords - common_words
        
        # Add specific location mappings for better matching
        if 'tel' in location_keywords or 'aviv' in location_keywords:
            location_keywords.update(['tel', 'aviv', 'israel'])
        if 'israel' in location_keywords:
            location_keywords.update(['israel', 'israeli'])
        
        filtered_jobs = []
        for job in jobs:
            # Check multiple location fields
            job_location_text = " ".join([
                (job.get("location") or "").lower(),
                (job.get("city") or "").lower(),
                (job.get("state") or "").lower(),
                (job.get("country") or "").lower()
            ])
            
            # Check if any location keywords match the job location
            matches_location = False
            for keyword in location_keywords:
                if keyword in job_location_text:
                    matches_location = True
                    break
            
            # Also include remote jobs
            is_remote = job.get("is_remote", False) or "remote" in job_location_text
            
            # Special handling for specific countries/regions
            is_country_match = False
            if 'israel' in location_keywords:
                is_country_match = 'israel' in job_location_text or 'il' in (job.get("country") or "").lower()
            
            # Include job if it matches location, is remote, or matches country
            if matches_location or is_remote or is_country_match:
                filtered_jobs.append(job)
        
        # Log the filtering results for debugging
        logger.info(f"Location filtering for '{original_location}': {len(jobs)} -> {len(filtered_jobs)} jobs")
        
        # If filtering removed too many jobs, try a more lenient approach
        if len(filtered_jobs) == 0:
            logger.warning("Strict filtering removed all jobs, trying lenient filtering...")
            
            # More lenient filtering - include any job with remote possibility or partial matches
            for job in jobs:
                job_location_text = " ".join([
                    (job.get("location") or "").lower(),
                    (job.get("city") or "").lower(),
                    (job.get("country") or "").lower()
                ])
                
                # Include remote jobs or jobs that might be relevant
                if (job.get("is_remote", False) or 
                    "remote" in job_location_text or
                    any(keyword in job_location_text for keyword in ['global', 'worldwide', 'international'])):
                    filtered_jobs.append(job)
            
            if len(filtered_jobs) > 0:
                logger.info(f"Lenient filtering found {len(filtered_jobs)} remote/international jobs")
                return filtered_jobs
            else:
                logger.warning("No relevant jobs found, returning original results with location disclaimer")
                return jobs
        
        return filtered_jobs
        
    def search_jobs(self, query: str, location: Optional[str] = None, 
                   employment_types: Optional[str] = "FULLTIME", 
                   experience_level: Optional[str] = None,
                   num_pages: int = 1, 
                   date_posted: Optional[str] = "all") -> List[Dict[str, Any]]:
        """
        Search for jobs using JSearch API
        
        Args:
            query: Job search query (e.g., "software engineer", "data scientist")
            location: Location filter (e.g., "New York, NY", "Remote")
            employment_types: Employment types (FULLTIME, PARTTIME, INTERN, CONTRACTOR)
            experience_level: Experience level filter (internship, entry_level, associate, mid_senior, director, executive)
            num_pages: Number of pages to fetch (each page has ~10 jobs)
            date_posted: Date filter (all, today, 3days, week, month)
            
        Returns:
            List of job dictionaries with standardized format
        """
        try:
            url = f"{self.base_url}/search"
            
            # Normalize location for better API results
            normalized_location = self._normalize_location(location) if location else None
            
            # Map experience level to employment types and query modifiers
            experience_employment_mapping = {
                "internship": ("INTERN", "intern internship"),
                "entry_level": ("FULLTIME", "entry level junior"),
                "associate": ("FULLTIME", "associate"),
                "mid_senior": ("FULLTIME", "senior mid level"),
                "director": ("FULLTIME", "director manager"),
                "executive": ("FULLTIME", "executive VP president")
            }
            
            # Adjust employment types and query based on experience level
            if experience_level and experience_level in experience_employment_mapping:
                employment_types, level_terms = experience_employment_mapping[experience_level]
                enhanced_query = f"{query} {level_terms}"
                logger.info(f"Applied experience level filter '{experience_level}': employment_types={employment_types}, level_terms='{level_terms}'")
            else:
                enhanced_query = query
            
            # Include location in query for better results since JSearch API location parameter is unreliable
            if normalized_location:
                enhanced_query = f"{enhanced_query} {normalized_location}"
            
            params = {
                "query": enhanced_query,
                "page": "1",
                "num_pages": str(num_pages),
                "date_posted": date_posted,
                "employment_types": employment_types
            }
            
            logger.info(f"Searching jobs with enhanced query: {enhanced_query}")
            
            # First try with location-specific query
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get("status") == "OK":
                logger.error(f"JSearch API error: {data.get('request_info', {}).get('message', 'Unknown error')}")
                return []
                
            jobs = data.get("data", [])
            
            # If no results for international location, try with remote/global search
            if len(jobs) == 0 and location and normalized_location and not self._is_us_location(normalized_location):
                logger.info(f"No results for {normalized_location}, trying remote/global search...")
                
                # Build remote query with experience level if specified
                remote_query = f"{query} remote"
                if experience_level and experience_level in experience_employment_mapping:
                    _, level_terms = experience_employment_mapping[experience_level]
                    remote_query = f"{query} {level_terms} remote"
                
                # Try searching for remote jobs in the same field
                remote_params = {
                    "query": remote_query,
                    "page": "1", 
                    "num_pages": str(num_pages),
                    "date_posted": date_posted,
                    "employment_types": employment_types
                }
                
                remote_response = requests.get(url, headers=self.headers, params=remote_params, timeout=30)
                remote_response.raise_for_status()
                remote_data = remote_response.json()
                
                if remote_data.get("status") == "OK":
                    remote_jobs = remote_data.get("data", [])
                    if remote_jobs:
                        logger.info(f"Found {len(remote_jobs)} remote jobs as fallback")
                        jobs = remote_jobs
            
            # Transform to standardized format
            standardized_jobs = []
            for job in jobs:
                # Build comprehensive location string for better filtering
                job_location_parts = []
                if job.get("job_city"):
                    job_location_parts.append(job.get("job_city"))
                if job.get("job_state"):
                    job_location_parts.append(job.get("job_state"))
                if job.get("job_country"):
                    job_location_parts.append(job.get("job_country"))
                
                full_location = ", ".join(job_location_parts) if job_location_parts else ""
                
                standardized_job = {
                    "title": job.get("job_title", ""),
                    "company": job.get("employer_name", ""),
                    "location": full_location,
                    "city": job.get("job_city", ""),
                    "state": job.get("job_state", ""),
                    "country": job.get("job_country", ""),
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
            
            # Light location filtering since we already enhanced the query
            if location and normalized_location and len(standardized_jobs) > 5:
                filtered_jobs = self._light_filter_jobs_by_location(standardized_jobs, location, normalized_location)
                if len(filtered_jobs) >= 3:  # Only apply if we still have reasonable results
                    standardized_jobs = filtered_jobs
                
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
    
    def _light_filter_jobs_by_location(self, jobs: List[Dict[str, Any]], original_location: str, normalized_location: str) -> List[Dict[str, Any]]:
        """
        Light location filtering that's less aggressive than the strict filter
        
        Args:
            jobs: List of job dictionaries
            original_location: Original location string from user
            normalized_location: Normalized location string
            
        Returns:
            Lightly filtered list of jobs
        """
        if not jobs or not original_location:
            return jobs
        
        # Extract main location keywords
        location_keywords = set()
        for loc in [original_location.lower(), normalized_location.lower()]:
            words = loc.replace(',', ' ').replace('-', ' ').split()
            location_keywords.update(words)
        
        # Remove common words
        common_words = {'in', 'the', 'at', 'of', 'and', 'or', 'a', 'an'}
        location_keywords = location_keywords - common_words
        
        # Prioritize jobs that match location, but don't exclude others completely
        priority_jobs = []
        other_jobs = []
        
        for job in jobs:
            job_location_text = " ".join([
                (job.get("location") or "").lower(),
                (job.get("city") or "").lower(),
                (job.get("country") or "").lower()
            ])
            
            # Check for matches or remote opportunities
            has_location_match = any(keyword in job_location_text for keyword in location_keywords)
            is_remote = job.get("is_remote", False) or "remote" in job_location_text
            
            if has_location_match or is_remote:
                priority_jobs.append(job)
            else:
                other_jobs.append(job)
        
        # Return priority jobs first, then others if we need more results
        result = priority_jobs + other_jobs[:max(0, 10 - len(priority_jobs))]
        
        logger.info(f"Light filtering: {len(priority_jobs)} priority jobs, {len(result)} total returned")
        return result

# Global instance
jsearch_service = JSearchService()