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
    
    def _get_experience_keywords(self, experience_level: str) -> str:
        """
        Convert experience level to search keywords
        
        Args:
            experience_level: Experience level filter (entry_level, mid_level, senior, etc.)
            
        Returns:
            Keywords to add to search query for experience filtering
        """
        experience_mappings = {
            "internship": "intern internship student",
            "entry_level": "entry level junior graduate new grad",
            "mid_level": "mid level experienced",
            "mid_senior": "senior experienced lead",
            "senior": "senior lead principal staff",
            "executive": "director executive VP manager"
        }
        
        return experience_mappings.get(experience_level.lower(), "")
    
    def _should_add_experience_to_query(self, location: Optional[str]) -> bool:
        """
        Determine if experience level keywords should be added to the search query
        Only add for English-speaking regions to avoid reducing results for international searches
        
        Args:
            location: Normalized location string
            
        Returns:
            True if experience keywords should be added to query, False otherwise
        """
        if not location:
            return True  # Default to adding keywords if no location specified
        
        location_lower = location.lower()
        
        # English-speaking countries/regions where experience keywords work well
        english_regions = [
            "united states", "usa", "us", "america",
            "canada", "uk", "united kingdom", "england", "scotland", "wales",
            "australia", "new zealand", "ireland", "south africa"
        ]
        
        # US states and major English-speaking cities
        us_regions = [
            "new york", "california", "texas", "florida", "washington",
            "seattle", "san francisco", "los angeles", "chicago", "boston",
            "atlanta", "denver", "austin", "miami", "philadelphia"
        ]
        
        # Check if location matches English-speaking regions
        for region in english_regions + us_regions:
            if region in location_lower:
                return True
        
        return False  # For international locations, rely on post-search filtering only
    
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
            num_pages: Number of pages to fetch (each page has ~10 jobs)
            date_posted: Date filter (all, today, 3days, week, month)
            
        Returns:
            List of job dictionaries with standardized format
        """
        try:
            url = f"{self.base_url}/search"
            
            # Normalize location for better API results
            normalized_location = self._normalize_location(location) if location else None
            
            # Include location in query for better results since JSearch API location parameter is unreliable
            enhanced_query = query
            if normalized_location:
                enhanced_query = f"{query} {normalized_location}"
            
            # Add experience level keywords to query only for US/English-speaking regions
            if experience_level and self._should_add_experience_to_query(normalized_location):
                experience_keywords = self._get_experience_keywords(experience_level)
                if experience_keywords:
                    enhanced_query = f"{enhanced_query} {experience_keywords}"
            
            params = {
                "query": enhanced_query,
                "page": "1",
                "num_pages": str(num_pages),
                "date_posted": date_posted,
                "employment_types": employment_types
            }
            
            logger.info(f"Searching jobs with enhanced query: {enhanced_query}")
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get("status") == "OK":
                logger.error(f"JSearch API error: {data.get('request_info', {}).get('message', 'Unknown error')}")
                return []
                
            jobs = data.get("data", [])
            logger.info(f"Initial search returned {len(jobs)} jobs for query: {enhanced_query}")
            
            # For international locations, always try multiple search strategies for better coverage
            if normalized_location and not self._should_add_experience_to_query(normalized_location):
                if len(jobs) < 5:  # If we have fewer than 5 jobs, try to supplement with more
                    logger.info(f"Limited results for {normalized_location} ({len(jobs)} jobs), trying supplementary search strategies")
                
                # Try search without location restriction but with global/international keywords
                global_params = {
                    "query": f"{query} international global remote worldwide",
                    "page": "1", 
                    "num_pages": str(num_pages),
                    "date_posted": date_posted,
                    "employment_types": employment_types
                }
                
                global_response = requests.get(url, headers=self.headers, params=global_params, timeout=30)
                if global_response.status_code == 200:
                    global_data = global_response.json()
                    if global_data.get("status") == "OK":
                        potential_jobs = global_data.get("data", [])
                        
                        # Filter for truly remote or international opportunities
                        filtered_jobs = []
                        for job in potential_jobs:
                            job_title = (job.get("job_title", "") or "").lower()
                            job_desc = (job.get("job_description", "") or "").lower()
                            is_remote = job.get("job_is_remote", False)
                            
                            # Look for indicators of international/remote opportunities
                            international_indicators = [
                                "remote", "worldwide", "global", "international", 
                                "anywhere", "work from home", "distributed", "virtual"
                            ]
                            
                            is_international = any(indicator in job_title or indicator in job_desc 
                                                 for indicator in international_indicators)
                            
                            if is_remote or is_international:
                                filtered_jobs.append(job)
                        
                        if filtered_jobs:
                            # Combine original jobs with supplementary results
                            combined_jobs = list(jobs) + filtered_jobs
                            # Remove duplicates based on job_id or title+company
                            seen = set()
                            unique_jobs = []
                            for job in combined_jobs:
                                job_key = (job.get("job_id", ""), job.get("job_title", ""), job.get("employer_name", ""))
                                if job_key not in seen:
                                    seen.add(job_key)
                                    unique_jobs.append(job)
                            
                            jobs = unique_jobs[:10]  # Limit to 10 best matches
                            logger.info(f"Combined search found {len(jobs)} total opportunities ({len(filtered_jobs)} supplementary)")
            
            # Transform to standardized format and add metadata for international searches
            standardized_jobs = []
            is_international_location = normalized_location and not self._should_add_experience_to_query(normalized_location)
            
            # Add informational guidance for international locations with limited results
            if is_international_location and len(standardized_jobs) < 3:
                # Create an informational "job" entry to guide users
                info_job = {
                    "title": f"Job Search Tips for {normalized_location}",
                    "company": "Job Search Guidance",
                    "location": normalized_location,
                    "city": "",
                    "state": "",
                    "country": "",
                    "description": f"Our current job database focuses primarily on US markets with limited coverage for {normalized_location}. For better results in your region, we recommend: 1) Use local job boards like Jobs.ch (Switzerland), StepStone (Germany), or LinkedIn for international opportunities, 2) Search without location to find remote positions that accept international candidates, 3) Try broader search terms like your profession + 'remote' or 'international', 4) Consider major European cities like London, Berlin, or Amsterdam which may have better coverage.",
                    "url": "",
                    "posted_date": "",
                    "employment_type": "Guidance",
                    "salary_min": None,
                    "salary_max": None,
                    "currency": None,
                    "is_remote": False,
                    "job_id": "guidance",
                    "source": "system_guidance"
                }
                standardized_jobs.insert(0, info_job)  # Put guidance at the top
                logger.info(f"Added guidance message for limited coverage in {normalized_location}")
            
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
            
            # Apply experience level filtering if specified
            if experience_level and len(standardized_jobs) > 0:
                experience_filtered_jobs = self._filter_jobs_by_experience(standardized_jobs, experience_level)
                if len(experience_filtered_jobs) >= 3:  # Keep reasonable number of results
                    standardized_jobs = experience_filtered_jobs
                
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
    
    def _filter_jobs_by_experience(self, jobs: List[Dict[str, Any]], experience_level: str) -> List[Dict[str, Any]]:
        """
        Filter jobs by experience level based on job title and description
        
        Args:
            jobs: List of job dictionaries
            experience_level: Experience level filter
            
        Returns:
            Filtered list of jobs matching experience level
        """
        if not jobs or not experience_level:
            return jobs
        
        # Get experience keywords for filtering
        experience_keywords = self._get_experience_keywords(experience_level).split()
        if not experience_keywords:
            return jobs
        
        # Define anti-patterns (keywords that contradict the experience level)
        anti_patterns = {
            "internship": ["senior", "lead", "principal", "director", "manager", "experienced"],
            "entry_level": ["senior", "lead", "principal", "director", "sr", "staff"],
            "mid_level": ["intern", "junior", "new grad"],
            "mid_senior": ["intern", "junior", "new grad", "entry"],
            "senior": ["intern", "junior", "new grad", "entry", "associate"],
            "executive": ["intern", "junior", "entry", "associate"]
        }
        
        filtered_jobs = []
        for job in jobs:
            job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
            
            # Check if job matches experience level keywords
            has_positive_match = any(keyword.lower() in job_text for keyword in experience_keywords)
            
            # Check for anti-patterns
            anti_keywords = anti_patterns.get(experience_level.lower(), [])
            has_negative_match = any(anti_keyword in job_text for anti_keyword in anti_keywords)
            
            # Include job if it has positive matches and no strong negative matches
            if has_positive_match or not has_negative_match:
                filtered_jobs.append(job)
        
        logger.info(f"Experience filtering ({experience_level}): {len(jobs)} -> {len(filtered_jobs)} jobs")
        return filtered_jobs

# Global instance
jsearch_service = JSearchService()