"""
Free Resume Optimization Service
Uses rule-based analysis and free AI models for resume optimization
No API costs or external dependencies required
"""

import json
import re
import logging
from typing import List, Dict, Any
from fastapi import HTTPException, status
from schemas import ResumeOptimizationRequest, ResumeOptimizationResponse

logger = logging.getLogger(__name__)

class FreeResumeOptimizer:
    """
    Free resume optimization service using rule-based analysis
    and local processing without external API costs
    """
    
    def __init__(self):
        """Initialize the free resume optimizer"""
        self.action_verbs = [
            "achieved", "analyzed", "built", "created", "designed", "developed",
            "enhanced", "established", "executed", "implemented", "improved",
            "increased", "led", "managed", "optimized", "produced", "reduced",
            "resolved", "streamlined", "supervised", "transformed"
        ]
        
        self.technical_keywords = {
            "software": ["python", "javascript", "react", "node.js", "sql", "git", "api", "aws", "docker"],
            "data": ["sql", "python", "excel", "tableau", "analytics", "statistics", "machine learning"],
            "management": ["leadership", "project management", "agile", "scrum", "team", "strategy"],
            "marketing": ["seo", "social media", "content", "campaigns", "analytics", "branding"]
        }
        
        self.common_improvements = [
            "Use action verbs to start bullet points",
            "Quantify achievements with numbers and percentages",
            "Include relevant technical keywords",
            "Keep bullet points concise and impactful",
            "Focus on accomplishments rather than job duties",
            "Use consistent formatting throughout",
            "Include relevant certifications and skills",
            "Tailor content to match job requirements"
        ]

    def optimize_resume(self, request: ResumeOptimizationRequest) -> ResumeOptimizationResponse:
        """
        Optimize resume content using rule-based analysis
        """
        try:
            resume_content = request.resume_content
            job_description = request.job_description or ""
            
            # Analyze current resume
            analysis = self._analyze_resume_content(resume_content)
            
            # Generate optimized content
            optimized_content = self._optimize_content(resume_content, job_description, analysis)
            
            # Generate suggestions
            suggestions = self._generate_suggestions(analysis, job_description)
            
            # Calculate improvement score
            score = self._calculate_score(analysis)
            
            return ResumeOptimizationResponse(
                optimized_content=optimized_content,
                suggestions=suggestions,
                score=score
            )
            
        except Exception as e:
            logger.error(f"Free resume optimization error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Resume optimization failed: {str(e)}"
            )

    def _analyze_resume_content(self, content: str) -> Dict[str, Any]:
        """Analyze resume content for strengths and weaknesses"""
        analysis = {
            "word_count": len(content.split()),
            "has_action_verbs": 0,
            "has_numbers": 0,
            "bullet_points": 0,
            "sections": 0,
            "contact_info": False,
            "skills_section": False,
            "experience_section": False,
            "education_section": False
        }
        
        # Count action verbs
        for verb in self.action_verbs:
            if verb.lower() in content.lower():
                analysis["has_action_verbs"] += 1
        
        # Count numbers (achievements)
        numbers = re.findall(r'\d+', content)
        analysis["has_numbers"] = len(numbers)
        
        # Count bullet points
        analysis["bullet_points"] = content.count('•') + content.count('-') + content.count('*')
        
        # Check for sections
        content_lower = content.lower()
        if any(word in content_lower for word in ['email', '@', 'phone', 'tel']):
            analysis["contact_info"] = True
        if any(word in content_lower for word in ['skills', 'technologies', 'technical']):
            analysis["skills_section"] = True
        if any(word in content_lower for word in ['experience', 'work', 'employment']):
            analysis["experience_section"] = True
        if any(word in content_lower for word in ['education', 'degree', 'university', 'college']):
            analysis["education_section"] = True
            
        # Count sections
        analysis["sections"] = sum([
            analysis["contact_info"],
            analysis["skills_section"], 
            analysis["experience_section"],
            analysis["education_section"]
        ])
        
        return analysis

    def _optimize_content(self, content: str, job_description: str, analysis: Dict[str, Any]) -> str:
        """Generate optimized resume content"""
        lines = content.split('\n')
        optimized_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                optimized_lines.append('')
                continue
                
            # Optimize bullet points
            if line.startswith(('-', '•', '*')):
                optimized_line = self._optimize_bullet_point(line, job_description)
                optimized_lines.append(optimized_line)
            else:
                optimized_lines.append(line)
        
        # Add missing sections if needed
        optimized_content = '\n'.join(optimized_lines)
        
        if not analysis["skills_section"] and job_description:
            skills_suggestion = self._suggest_skills_section(job_description)
            optimized_content += f"\n\nSKILLS:\n{skills_suggestion}"
        
        return optimized_content

    def _optimize_bullet_point(self, bullet: str, job_description: str) -> str:
        """Optimize a single bullet point"""
        # Remove bullet marker
        content = re.sub(r'^[-•*]\s*', '', bullet)
        
        # Check if it starts with an action verb
        words = content.split()
        if words and words[0].lower() not in [verb.lower() for verb in self.action_verbs]:
            # Try to add an action verb
            if any(word in content.lower() for word in ['built', 'created', 'developed']):
                pass  # Already has action words
            elif 'responsible for' in content.lower():
                content = content.replace('Responsible for', 'Managed')
                content = content.replace('responsible for', 'managed')
            elif content.lower().startswith('worked on'):
                content = content.replace('Worked on', 'Developed', 1)
                content = content.replace('worked on', 'developed', 1)
        
        return f"• {content}"

    def _suggest_skills_section(self, job_description: str) -> str:
        """Suggest skills based on job description"""
        suggested_skills = []
        job_desc_lower = job_description.lower()
        
        for category, keywords in self.technical_keywords.items():
            for keyword in keywords:
                if keyword.lower() in job_desc_lower:
                    suggested_skills.append(keyword.title())
        
        if suggested_skills:
            return "• " + "\n• ".join(suggested_skills[:8])
        else:
            return "• Programming Languages\n• Project Management\n• Problem Solving\n• Team Collaboration"

    def _generate_suggestions(self, analysis: Dict[str, Any], job_description: str) -> List[str]:
        """Generate improvement suggestions based on analysis"""
        suggestions = []
        
        if analysis["has_action_verbs"] < 3:
            suggestions.append("Add more action verbs to make your achievements more impactful")
        
        if analysis["has_numbers"] < 2:
            suggestions.append("Include quantifiable achievements with numbers and percentages")
        
        if analysis["bullet_points"] < 3:
            suggestions.append("Use bullet points to improve readability and highlight key achievements")
        
        if not analysis["skills_section"]:
            suggestions.append("Add a dedicated skills section with relevant technical and soft skills")
        
        if analysis["word_count"] < 200:
            suggestions.append("Expand your resume with more detailed descriptions of your experience")
        elif analysis["word_count"] > 800:
            suggestions.append("Consider condensing your resume to focus on the most relevant information")
        
        if job_description:
            suggestions.append("Tailor your resume keywords to match the job description requirements")
        
        # Add random suggestions from common improvements
        suggestions.extend(self.common_improvements[:3])
        
        return suggestions[:6]  # Limit to 6 suggestions

    def _calculate_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate resume quality score"""
        score = 0.0
        
        # Base score for having content
        if analysis["word_count"] > 100:
            score += 20
        
        # Action verbs bonus
        score += min(analysis["has_action_verbs"] * 5, 25)
        
        # Numbers/achievements bonus
        score += min(analysis["has_numbers"] * 3, 15)
        
        # Structure bonus
        score += analysis["sections"] * 10
        
        # Formatting bonus
        if analysis["bullet_points"] > 0:
            score += 10
        
        # Ensure score is between 0 and 100
        return min(max(score, 0), 100) / 100

    def analyze_resume(self, resume_content: str) -> Dict[str, Any]:
        """Analyze resume and provide detailed feedback"""
        analysis = self._analyze_resume_content(resume_content)
        score = self._calculate_score(analysis)
        
        strengths = []
        weaknesses = []
        
        if analysis["has_action_verbs"] >= 3:
            strengths.append("Good use of action verbs")
        else:
            weaknesses.append("Limited use of action verbs")
            
        if analysis["has_numbers"] >= 2:
            strengths.append("Includes quantifiable achievements")
        else:
            weaknesses.append("Lacks quantified achievements")
            
        if analysis["sections"] >= 3:
            strengths.append("Well-structured with multiple sections")
        else:
            weaknesses.append("Could benefit from better organization")
        
        return {
            "score": score,
            "word_count": analysis["word_count"],
            "strengths": strengths,
            "weaknesses": weaknesses,
            "suggestions": self._generate_suggestions(analysis, ""),
            "ats_friendly": score > 0.6,
            "readability": "Good" if analysis["bullet_points"] > 0 else "Needs improvement"
        }

# Global instance
free_resume_optimizer_service = FreeResumeOptimizer()