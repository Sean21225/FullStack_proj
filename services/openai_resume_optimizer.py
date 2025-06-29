"""
Resume optimization service module
Integrates with OpenAI ChatGPT for AI-powered resume optimization
"""

import os
import json
import logging
from typing import List
from fastapi import HTTPException, status
from openai import OpenAI

from schemas import ResumeOptimizationRequest, ResumeOptimizationResponse

logger = logging.getLogger(__name__)


class OpenAIResumeOptimizerService:
    """
    Service class for resume optimization operations
    Uses OpenAI ChatGPT for intelligent resume analysis and optimization
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found. Resume optimization will not work.")
        
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        
    def _get_optimization_prompt(self, resume_content: str, job_description: str = "", optimization_type: str = "general") -> str:
        """
        Generate the appropriate prompt for resume optimization based on type
        """
        base_prompt = f"""You are an expert resume consultant and career advisor. Please analyze and optimize the following resume.

Resume Content:
{resume_content}

"""
        
        if job_description and job_description.strip():
            base_prompt += f"""Job Description to tailor for:
{job_description}

"""
        
        optimization_instructions = {
            "general": "Provide general improvements to make the resume more professional, impactful, and well-structured.",
            "ats": "Optimize for Applicant Tracking Systems (ATS) by improving keyword usage, formatting, and structure.",
            "keywords": "Enhance keyword density and relevance for better searchability and matching.",
            "format": "Improve the overall format, structure, and presentation of the resume."
        }
        
        instruction = optimization_instructions.get(optimization_type, optimization_instructions["general"])
        
        base_prompt += f"""Optimization Focus: {instruction}

Please provide your response in JSON format with the following structure:
{{
    "optimized_content": "The improved resume content with better formatting, stronger action verbs, and enhanced descriptions",
    "suggestions": ["Specific suggestion 1", "Specific suggestion 2", "Specific suggestion 3"],
    "score": 0.85
}}

The score should be between 0 and 1, representing the overall quality of the optimized resume.
Focus on:
- Strong action verbs and quantified achievements
- Clear, concise language
- Proper formatting and structure
- Relevant keywords for the role
- Professional presentation
"""
        
        return base_prompt
    
    def optimize_resume(self, request: ResumeOptimizationRequest) -> ResumeOptimizationResponse:
        """
        Optimize resume content using OpenAI ChatGPT
        Returns optimized content with suggestions and scoring
        """
        if not self.client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="OpenAI API key not configured. Please provide OPENAI_API_KEY."
            )
        
        try:
            prompt = self._get_optimization_prompt(
                request.resume_content,
                request.job_description or "",
                request.optimization_type
            )
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume consultant. Always respond with valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=2000,
                temperature=0.7
            )
            
            # Parse the response
            response_content = response.choices[0].message.content
            if not response_content:
                raise ValueError("Empty response from OpenAI")
            result = json.loads(response_content)
            
            return ResumeOptimizationResponse(
                optimized_content=result.get("optimized_content", request.resume_content),
                suggestions=result.get("suggestions", []),
                score=result.get("score", 0.75)
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process optimization results"
            )
        except Exception as e:
            logger.error(f"OpenAI resume optimization error: {str(e)}")
            if "insufficient_quota" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="OpenAI API quota exceeded. Please check your billing."
                )
            elif "invalid_api_key" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Invalid OpenAI API key. Please verify your credentials."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Resume optimization failed"
                )
    
    def analyze_resume(self, resume_content: str) -> dict:
        """
        Analyze a resume and provide detailed insights
        """
        if not self.client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="OpenAI API key not configured. Please provide OPENAI_API_KEY."
            )
        
        try:
            prompt = f"""Analyze the following resume and provide detailed insights:

{resume_content}

Provide your analysis in JSON format:
{{
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "recommendations": ["Recommendation 1", "Recommendation 2"],
    "overall_score": 0.75,
    "ats_score": 0.80,
    "keyword_density": "Medium",
    "readability": "Good"
}}
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume analyst. Always respond with valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=1500,
                temperature=0.3
            )
            
            response_content = response.choices[0].message.content
            if not response_content:
                raise ValueError("Empty response from OpenAI")
            return json.loads(response_content)
            
        except Exception as e:
            logger.error(f"Resume analysis error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Resume analysis failed"
            )


# Create singleton instance
openai_resume_optimizer_service = OpenAIResumeOptimizerService()