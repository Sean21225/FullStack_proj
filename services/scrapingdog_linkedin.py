"""
ScrapingDog LinkedIn scraper service
Integrates with ScrapingDog API for LinkedIn job and company data
"""

import os
import logging
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
import requests
from schemas import LinkedInJobRequest, LinkedInJobResponse, LinkedInCompanyRequest, LinkedInCompanyResponse

logger = logging.getLogger(__name__)


class ScrapingDogLinkedInService:
    """
    Service class for LinkedIn data scraping using ScrapingDog API
    """
    
    def __init__(self):
        self.api_key = os.getenv("LINKEDIN_SCRAPER_API_KEY", "demo_key")
        self.base_url = "https://api.scrapingdog.com"
        self.timeout = 45
        
    def search_jobs(self, request: LinkedInJobRequest) -> List[LinkedInJobResponse]:
        """
        Search for jobs on LinkedIn using ScrapingDog API
        Returns a list of job postings matching the criteria
        """
        try:
            # ScrapingDog API parameters
            params = {
                "api_key": self.api_key,
                "field": request.keywords,  # ScrapingDog uses 'field' instead of 'keywords'
                "page": 1
            }
            
            # Add location if provided
            if request.location:
                params["location"] = request.location
                
            # Add limit (ScrapingDog supports up to 50 per request)
            if request.limit and request.limit <= 50:
                params["limit"] = request.limit
            
            # Make request to ScrapingDog LinkedIn Jobs API
            url = f"{self.base_url}/linkedinjobs"
            
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="LinkedIn scraper service authentication failed - please check API key"
                )
            elif response.status_code == 429:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="LinkedIn scraper service rate limit exceeded"
                )
            elif response.status_code >= 400:
                logger.error(f"ScrapingDog API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"LinkedIn scraper service error: {response.status_code}"
                )
            
            jobs_data = response.json()
            if not isinstance(jobs_data, list):
                jobs_data = []
                
            jobs = []
            
            for job_data in jobs_data:
                job = LinkedInJobResponse(
                    title=job_data.get("job_position", ""),
                    company=job_data.get("company_name", ""),
                    location=job_data.get("job_location", ""),
                    description=f"Posted: {job_data.get('job_posting_date', '')} | Job ID: {job_data.get('job_id', '')}",
                    url=job_data.get("job_link", ""),
                    posted_date=job_data.get("job_posting_date")
                )
                jobs.append(job)
                
            return jobs
            
        except HTTPException:
            raise
        except requests.exceptions.Timeout:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="LinkedIn scraper service timeout"
            )
        except requests.exceptions.ConnectionError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LinkedIn scraper service unavailable"
            )
        except Exception as e:
            logger.error(f"Job search failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"LinkedIn scraper service error: {str(e)}"
            )
    
    def get_company_info(self, request: LinkedInCompanyRequest) -> LinkedInCompanyResponse:
        """
        Get company information from LinkedIn using ScrapingDog API
        Note: ScrapingDog may not have a dedicated company endpoint, 
        so this returns basic info or searches for the company
        """
        try:
            # For now, return a basic response since ScrapingDog focuses on job listings
            # In a real implementation, you'd use their company scraping endpoint if available
            return LinkedInCompanyResponse(
                name=request.company_name,
                industry="Technology (estimated)",
                size="Unknown",
                description=f"Company information for {request.company_name} - detailed data requires company-specific scraping",
                website=None,
                headquarters="Unknown"
            )
            
        except Exception as e:
            logger.error(f"Company search failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Company lookup service error: {str(e)}"
            )


# Create global service instance
scrapingdog_linkedin_service = ScrapingDogLinkedInService()