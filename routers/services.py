"""
External services router
Handles resume optimization and LinkedIn scraping services
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

from database import get_db
from models import User, Resume
from schemas import (
    ResumeOptimizationRequest, ResumeOptimizationResponse,
    LinkedInJobRequest, LinkedInJobResponse,
    LinkedInCompanyRequest, LinkedInCompanyResponse
)
from auth import get_current_active_user
from services.resume_optimizer import resume_optimizer_service
from services.arbeitnow_api import arbeitnow_service
from services.google_jobs_api import adzuna_jobs_service
from services.company_data_api import CompanyDataService

router = APIRouter()

# Initialize company data service
company_data_service = CompanyDataService()


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
        # First try Arbeitnow API for European jobs (free, unlimited)
        jobs = arbeitnow_service.search_jobs(
            query=keywords,
            location=location,
            experience_level=experience_level,
            limit=limit
        )
        
        # If no results from Arbeitnow (especially for non-European locations), try Adzuna API
        if len(jobs) == 0 and location:
            logger.info(f"No results from Arbeitnow for location '{location}', trying Adzuna API")
            adzuna_jobs = adzuna_jobs_service.search_jobs(
                query=keywords,
                location=location,
                experience_level=experience_level,
                limit=limit
            )
            jobs.extend(adzuna_jobs)
        
        # If still no results and no location specified, try Adzuna for broader coverage
        elif len(jobs) < limit and not location:
            remaining_limit = limit - len(jobs)
            adzuna_jobs = adzuna_jobs_service.search_jobs(
                query=keywords,
                location=location,
                experience_level=experience_level,
                limit=remaining_limit
            )
            jobs.extend(adzuna_jobs)
        
        # Limit results as requested
        limited_jobs = jobs[:limit] if jobs else []
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
    Get comprehensive company information using multiple data sources
    Returns detailed company data including industry, size, and financial information
    """
    try:
        # Use enhanced company data service for comprehensive information
        company_info = company_data_service.get_company_info(company_name)
        
        return {
            "name": company_info.get("name", company_name),
            "industry": company_info.get("industry", "Information not available"),
            "size": company_info.get("size", "Company size not disclosed"),
            "description": company_info.get("description", f"No detailed information available for {company_name}"),
            "website": company_info.get("website"),
            "headquarters": company_info.get("headquarters", "Location not disclosed")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Company lookup error: {str(e)}")
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
        # Use Arbeitnow API to get trending job types
        # Since Arbeitnow doesn't have a specific trending endpoint, we'll search for popular tech terms
        popular_terms = ["software engineer", "data scientist", "product manager", "devops", "frontend developer"]
        trending_data = []
        
        for term in popular_terms:
            jobs = arbeitnow_service.search_jobs(query=term, location=location, limit=5)
            if jobs:
                trending_data.append({
                    "title": term.title(),
                    "count": len(jobs),
                    "growth": "stable"  # Static data since we don't have historical trends
                })
        
        return {
            "trending_jobs": trending_data,
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