"""
External services router
Handles resume optimization and LinkedIn scraping services
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import User, Resume
from schemas import (
    ResumeOptimizationRequest, ResumeOptimizationResponse,
    LinkedInJobRequest, LinkedInJobResponse,
    LinkedInCompanyRequest, LinkedInCompanyResponse
)
from auth import get_current_active_user
from services.resume_optimizer import resume_optimizer_service
from services.jsearch_api import jsearch_service

router = APIRouter()


@router.post("/optimize-resume", response_model=ResumeOptimizationResponse)
async def optimize_resume_frontend(
    request: ResumeOptimizationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Optimize and tailor resume content - Frontend endpoint
    This is the endpoint called by the React frontend
    """
    try:
        # Call the resume optimizer service
        optimized_result = resume_optimizer_service.optimize_resume(request)
        return optimized_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume optimization failed: {str(e)}"
        )


@router.post("/api/optimizer/tailor", response_model=ResumeOptimizationResponse)
async def optimize_resume(
    request: ResumeOptimizationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Optimize and tailor resume content using AI service
    Integrates with external resume optimization API
    """
    try:
        # Call the resume optimizer service
        optimized_result = resume_optimizer_service.optimize_resume(request)
        return optimized_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume optimization failed: {str(e)}"
        )


@router.get("/api/optimizer/analyze/{resume_id}")
async def analyze_resume(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Analyze a user's resume and provide insights
    Returns detailed analysis including strengths and weaknesses
    """
    try:
        # Get the resume
        resume = db.query(Resume).filter(
            Resume.resume_id == resume_id,
            Resume.user_id == current_user.user_id
        ).first()
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        # Analyze the resume content
        analysis = resume_optimizer_service.analyze_resume(resume.content)
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume analysis failed: {str(e)}"
        )


@router.get("/api/suggestions/jobs", response_model=List[LinkedInJobResponse])
async def get_job_suggestions(
    keywords: str,
    location: Optional[str] = None,
    experience_level: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get job suggestions from LinkedIn based on keywords and location
    Searches for relevant job postings
    """
    try:
        # Calculate number of pages needed based on limit
        # JSearch API returns approximately 10 jobs per page
        jobs_per_page = 10
        num_pages = max(1, (limit + jobs_per_page - 1) // jobs_per_page)  # Ceiling division
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Job search request: limit={limit}, calculated num_pages={num_pages}")
        
        # Use JSearch API to search for jobs from LinkedIn, Indeed, Glassdoor, etc.
        jobs = jsearch_service.search_jobs(
            query=keywords,
            location=location,
            experience_level=experience_level,
            num_pages=num_pages
        )
        
        # Limit results as requested
        limited_jobs = jobs[:limit] if jobs else []
        logger.info(f"Returning {len(limited_jobs)} jobs out of {len(jobs)} total jobs found")
        return limited_jobs
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job search failed: {str(e)}"
        )


@router.get("/api/suggestions/companies", response_model=LinkedInCompanyResponse)
async def get_company_information(
    company_name: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get company information from LinkedIn
    Returns detailed company data including industry and size
    """
    try:
        # Use JSearch API to get company information from job postings
        companies = jsearch_service.search_companies(company_name)
        
        if companies:
            # Return first matching company
            company = companies[0]
            return {
                "name": company["name"],
                "industry": "Technology",  # JSearch doesn't provide industry data
                "size": f"~{company['job_count']} current job openings",
                "description": f"Company with {company['job_count']} active job postings",
                "website": None,
                "headquarters": ", ".join(company["locations"][:3]) if company["locations"] else None
            }
        else:
            return {
                "name": company_name,
                "industry": "Unknown",
                "size": "No current job postings found",
                "description": f"No recent job postings found for {company_name}",
                "website": None,
                "headquarters": None
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Company search failed: {str(e)}"
        )


@router.get("/api/jobs/trending")
async def get_trending_jobs(
    location: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get trending job titles and market insights
    Helps users understand current job market demand
    """
    try:
        # Use JSearch API to get trending jobs
        trending_jobs = jsearch_service.get_trending_jobs(location=location)
        
        return {
            "trending_jobs": trending_jobs,
            "location": location,
            "timeframe": "last_week"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Trending jobs request failed: {str(e)}"
        )


@router.get("/api/keywords/{job_title}")
async def get_job_keywords(
    job_title: str,
    job_description: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get recommended keywords for a specific job title
    Helps users optimize their resume for specific positions
    """
    try:
        keywords = resume_optimizer_service.get_keywords_for_job(job_title, job_description)
        return {
            "job_title": job_title,
            "recommended_keywords": keywords,
            "total_keywords": len(keywords)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Keyword extraction failed: {str(e)}"
        )


@router.post("/api/personalized/jobs", response_model=List[LinkedInJobResponse])
async def get_personalized_job_suggestions(
    skills: List[str],
    location: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get personalized job suggestions based on user skills
    Returns job recommendations tailored to user's skill set
    """
    try:
        if not skills:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one skill must be provided"
            )
        
        # Personalized job suggestions feature not available with current ScrapingDog service
        job_suggestions = []
        return job_suggestions
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Personalized job suggestions failed: {str(e)}"
        )