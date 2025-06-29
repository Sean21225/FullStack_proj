"""
Free Resume Optimization Service
Provides intelligent resume analysis and optimization without external API dependencies
Completely free to use with rule-based analysis and improvements
"""

import re
import logging
from typing import Optional, List, Dict, Any
from schemas import ResumeOptimizationRequest, ResumeOptimizationResponse

logger = logging.getLogger(__name__)


class ResumeOptimizerService:
    """
    Free rule-based resume optimization service
    Provides comprehensive resume analysis and improvements without API costs
    """
    
    def __init__(self):
        # Technical keywords database for different fields
        self.tech_keywords = {
            "software": [
                "Python", "JavaScript", "Java", "C++", "React", "Node.js", "SQL", "Git",
                "AWS", "Docker", "Kubernetes", "API", "REST", "GraphQL", "MongoDB", "PostgreSQL",
                "Machine Learning", "Data Science", "Agile", "Scrum", "CI/CD", "DevOps",
                "Frontend", "Backend", "Full-stack", "Microservices", "Cloud Computing"
            ],
            "data": [
                "Python", "R", "SQL", "Tableau", "Power BI", "Excel", "Statistics",
                "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Pandas",
                "NumPy", "Scikit-learn", "Data Visualization", "ETL", "Big Data", "Hadoop",
                "Spark", "Analytics", "Business Intelligence", "A/B Testing"
            ],
            "marketing": [
                "SEO", "SEM", "Google Analytics", "Facebook Ads", "Content Marketing",
                "Social Media", "Email Marketing", "Marketing Automation", "CRM",
                "Lead Generation", "Conversion Optimization", "Brand Management",
                "Digital Marketing", "Influencer Marketing", "Marketing Strategy"
            ]
        }
        
        # Action verbs for stronger impact
        self.action_verbs = [
            "Achieved", "Developed", "Implemented", "Led", "Managed", "Created",
            "Improved", "Increased", "Reduced", "Optimized", "Designed", "Built",
            "Launched", "Delivered", "Collaborated", "Analyzed", "Streamlined",
            "Enhanced", "Coordinated", "Executed", "Established", "Transformed"
        ]
        
        # Weak words to replace
        self.weak_words = {
            "responsible for": "managed",
            "worked on": "developed",
            "helped": "assisted",
            "did": "executed",
            "made": "created",
            "got": "achieved",
            "used": "utilized",
            "worked with": "collaborated with"
        }
    
    def _calculate_score(self, resume_content: str, job_description: Optional[str] = None) -> float:
        """Calculate resume score based on multiple factors"""
        score = 0.0
        
        # Length check (30% of score)
        word_count = len(resume_content.split())
        if 300 <= word_count <= 800:
            score += 30
        elif 200 <= word_count < 300 or 800 < word_count <= 1000:
            score += 20
        else:
            score += 10
        
        # Action verbs presence (25% of score)
        action_verb_count = sum(1 for verb in self.action_verbs if verb.lower() in resume_content.lower())
        score += min(25, action_verb_count * 2)
        
        # Technical keywords if job description provided (25% of score)
        if job_description:
            job_lower = job_description.lower()
            resume_lower = resume_content.lower()
            
            # Determine field based on job description
            field_keywords = []
            if any(word in job_lower for word in ["software", "developer", "engineer", "programming"]):
                field_keywords = self.tech_keywords["software"]
            elif any(word in job_lower for word in ["data", "analyst", "scientist", "analytics"]):
                field_keywords = self.tech_keywords["data"]
            elif any(word in job_lower for word in ["marketing", "marketing", "seo", "social"]):
                field_keywords = self.tech_keywords["marketing"]
            
            if field_keywords:
                matching_keywords = sum(1 for keyword in field_keywords if keyword.lower() in resume_lower)
                score += min(25, matching_keywords * 2)
            else:
                score += 15  # Base score if no specific field detected
        else:
            score += 15
        
        # Format and structure (20% of score)
        sections = ["experience", "education", "skills", "summary", "objective"]
        section_count = sum(1 for section in sections if section in resume_content.lower())
        score += min(20, section_count * 4)
        
        return min(100.0, score)
    
    def _generate_suggestions(self, resume_content: str, job_description: Optional[str] = None) -> List[str]:
        """Generate intelligent suggestions for resume improvement"""
        suggestions = []
        
        # Check for weak words
        for weak, strong in self.weak_words.items():
            if weak in resume_content.lower():
                suggestions.append(f"Replace '{weak}' with '{strong}' for stronger impact")
        
        # Check for action verbs
        action_verb_count = sum(1 for verb in self.action_verbs if verb.lower() in resume_content.lower())
        if action_verb_count < 3:
            suggestions.append("Add more action verbs like 'Developed', 'Implemented', 'Led' to strengthen your accomplishments")
        
        # Check length
        word_count = len(resume_content.split())
        if word_count < 300:
            suggestions.append("Consider expanding your resume with more details about your accomplishments and skills")
        elif word_count > 800:
            suggestions.append("Consider condensing your resume to focus on the most relevant achievements")
        
        # Check for quantified achievements
        if not re.search(r'\d+%|\$\d+|\d+\s+(years?|months?|projects?|users?|clients?)', resume_content):
            suggestions.append("Add quantified achievements (e.g., 'Increased sales by 25%', 'Managed team of 5 people')")
        
        # Job-specific suggestions
        if job_description:
            job_lower = job_description.lower()
            resume_lower = resume_content.lower()
            
            # Technical skills suggestions
            if "python" in job_lower and "python" not in resume_lower:
                suggestions.append("Consider highlighting Python experience if you have it")
            if "javascript" in job_lower and "javascript" not in resume_lower:
                suggestions.append("Consider mentioning JavaScript skills if relevant")
            if "leadership" in job_lower and "led" not in resume_lower and "managed" not in resume_lower:
                suggestions.append("Highlight any leadership or management experience")
        
        # Structure suggestions
        if "summary" not in resume_content.lower() and "objective" not in resume_content.lower():
            suggestions.append("Consider adding a professional summary at the top of your resume")
        
        return suggestions[:8]  # Limit to most important suggestions
    
    def _optimize_content(self, resume_content: str, job_description: Optional[str] = None) -> str:
        """Apply automatic optimizations to resume content"""
        optimized = resume_content
        
        # Replace weak words with stronger alternatives
        for weak, strong in self.weak_words.items():
            pattern = re.compile(re.escape(weak), re.IGNORECASE)
            optimized = pattern.sub(strong, optimized)
        
        # Improve bullet point formatting
        lines = optimized.split('\n')
        improved_lines = []
        
        for line in lines:
            stripped = line.strip()
            # If line starts with - or *, make sure it starts with an action verb
            if stripped.startswith(('- ', '* ', '• ')):
                content = stripped[2:].strip()
                if content and not any(content.lower().startswith(verb.lower()) for verb in self.action_verbs):
                    # Try to improve the bullet point
                    if content.lower().startswith('responsible for'):
                        content = content[len('responsible for'):].strip()
                        content = f"Managed {content}"
                    elif content.lower().startswith('worked on'):
                        content = content[len('worked on'):].strip()
                        content = f"Developed {content}"
                    improved_lines.append(f"{stripped[:2]}{content}")
                else:
                    improved_lines.append(line)
            else:
                improved_lines.append(line)
        
        return '\n'.join(improved_lines)
    
    def optimize_resume(self, request: ResumeOptimizationRequest) -> ResumeOptimizationResponse:
        """
        Optimize resume content using free rule-based analysis
        Returns optimized content with intelligent suggestions and scoring
        """
        try:
            # Apply content optimizations
            optimized_content = self._optimize_content(request.resume_content, request.job_description)
            
            # Generate improvement suggestions
            suggestions = self._generate_suggestions(request.resume_content, request.job_description)
            
            # Calculate quality score
            score = self._calculate_score(optimized_content, request.job_description)
            
            return ResumeOptimizationResponse(
                optimized_content=optimized_content,
                suggestions=suggestions,
                score=score
            )
            
        except Exception as e:
            logger.error(f"Resume optimization error: {str(e)}")
            return ResumeOptimizationResponse(
                optimized_content=request.resume_content,
                suggestions=["Unable to process optimization at this time"],
                score=50.0
            )
    
    def analyze_resume(self, resume_content: str) -> Dict[str, Any]:
        """
        Analyze resume and provide comprehensive insights using rule-based analysis
        Returns detailed analysis including strengths and weaknesses
        """
        try:
            overall_score = self._calculate_score(resume_content)
            word_count = len(resume_content.split())
            
            # Analyze different aspects
            keyword_score = self._analyze_keywords(resume_content)
            structure_score = self._analyze_structure(resume_content)
            content_score = self._analyze_content(resume_content)
            
            strengths = self._identify_strengths(resume_content)
            weaknesses = self._identify_weaknesses(resume_content)
            
            return {
                "overall_score": overall_score,
                "keyword_score": keyword_score,
                "structure_score": structure_score,
                "content_score": content_score,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "missing_keywords": self._suggest_missing_keywords(resume_content),
                "recommended_sections": self._suggest_sections(resume_content),
                "word_count": word_count,
                "reading_level": "Professional" if word_count > 300 else "Basic"
            }
            
        except Exception as e:
            logger.error(f"Resume analysis error: {str(e)}")
            return {
                "overall_score": 50.0,
                "keyword_score": 50.0,
                "structure_score": 50.0,
                "content_score": 50.0,
                "strengths": ["Resume received for analysis"],
                "weaknesses": ["Unable to complete full analysis"],
                "missing_keywords": [],
                "recommended_sections": [],
                "word_count": len(resume_content.split()),
                "reading_level": "Unknown"
            }
    
    def _analyze_keywords(self, resume_content: str) -> float:
        """Analyze keyword density and relevance"""
        all_keywords = []
        for field_keywords in self.tech_keywords.values():
            all_keywords.extend(field_keywords)
        
        resume_lower = resume_content.lower()
        found_keywords = sum(1 for keyword in all_keywords if keyword.lower() in resume_lower)
        return min(100.0, (found_keywords / len(all_keywords)) * 100 * 3)
    
    def _analyze_structure(self, resume_content: str) -> float:
        """Analyze resume structure and formatting"""
        sections = ["experience", "education", "skills", "summary", "objective", "projects"]
        section_count = sum(1 for section in sections if section in resume_content.lower())
        return min(100.0, (section_count / len(sections)) * 100)
    
    def _analyze_content(self, resume_content: str) -> float:
        """Analyze content quality"""
        action_verb_count = sum(1 for verb in self.action_verbs if verb.lower() in resume_content.lower())
        has_quantified = bool(re.search(r'\d+%|\$\d+|\d+\s+(years?|months?|projects?)', resume_content))
        
        score = min(50.0, action_verb_count * 5)
        if has_quantified:
            score += 25
        return min(100.0, score)
    
    def _identify_strengths(self, resume_content: str) -> List[str]:
        """Identify resume strengths"""
        strengths = []
        
        if len(resume_content.split()) > 300:
            strengths.append("Comprehensive content with good detail")
        
        action_verb_count = sum(1 for verb in self.action_verbs if verb.lower() in resume_content.lower())
        if action_verb_count >= 5:
            strengths.append("Strong use of action verbs")
        
        if re.search(r'\d+%|\$\d+|\d+\s+(years?|months?|projects?)', resume_content):
            strengths.append("Includes quantified achievements")
        
        sections = ["experience", "education", "skills"]
        if all(section in resume_content.lower() for section in sections):
            strengths.append("Well-structured with key sections")
        
        return strengths[:5]
    
    def _identify_weaknesses(self, resume_content: str) -> List[str]:
        """Identify areas for improvement"""
        weaknesses = []
        
        if len(resume_content.split()) < 200:
            weaknesses.append("Resume may be too brief")
        elif len(resume_content.split()) > 1000:
            weaknesses.append("Resume may be too lengthy")
        
        if any(weak in resume_content.lower() for weak in self.weak_words.keys()):
            weaknesses.append("Contains weak language that could be strengthened")
        
        if not re.search(r'\d+%|\$\d+|\d+\s+(years?|months?|projects?)', resume_content):
            weaknesses.append("Lacks quantified achievements")
        
        if "summary" not in resume_content.lower() and "objective" not in resume_content.lower():
            weaknesses.append("Missing professional summary")
        
        return weaknesses[:5]
    
    def _suggest_missing_keywords(self, resume_content: str) -> List[str]:
        """Suggest relevant keywords that might be missing"""
        resume_lower = resume_content.lower()
        missing = []
        
        # Suggest based on content analysis
        if "software" in resume_lower or "developer" in resume_lower:
            for keyword in self.tech_keywords["software"][:10]:
                if keyword.lower() not in resume_lower:
                    missing.append(keyword)
        
        return missing[:8]
    
    def _suggest_sections(self, resume_content: str) -> List[str]:
        """Suggest missing resume sections"""
        resume_lower = resume_content.lower()
        missing_sections = []
        
        recommended_sections = [
            ("Professional Summary", "summary"),
            ("Technical Skills", "skills"),
            ("Professional Experience", "experience"),
            ("Education", "education"),
            ("Projects", "projects"),
            ("Certifications", "certification")
        ]
        
        for section_name, keyword in recommended_sections:
            if keyword not in resume_lower:
                missing_sections.append(section_name)
        
        return missing_sections[:4]
    
    def get_keywords_for_job(self, job_title: str, job_description: Optional[str] = None) -> List[str]:
        """
        Get recommended keywords for a specific job using rule-based analysis
        Helps users optimize their resume for specific positions
        """
        try:
            keywords = []
            job_title_lower = job_title.lower()
            
            # Determine relevant keyword set based on job title
            if any(word in job_title_lower for word in ["software", "developer", "engineer", "programmer"]):
                keywords.extend(self.tech_keywords["software"][:15])
            elif any(word in job_title_lower for word in ["data", "analyst", "scientist"]):
                keywords.extend(self.tech_keywords["data"][:15])
            elif any(word in job_title_lower for word in ["marketing", "social", "seo"]):
                keywords.extend(self.tech_keywords["marketing"][:15])
            
            # Add general action verbs
            keywords.extend(self.action_verbs[:10])
            
            # Extract keywords from job description if provided
            if job_description:
                desc_words = re.findall(r'\b[A-Z][a-z]+\b', job_description)
                keywords.extend([word for word in desc_words if len(word) > 3][:10])
            
            return list(set(keywords))[:20]  # Remove duplicates and limit
            
        except Exception as e:
            logger.error(f"Keyword extraction error: {str(e)}")
            return ["Python", "JavaScript", "Communication", "Problem-solving", "Leadership"]


# Create global service instance
resume_optimizer_service = ResumeOptimizerService()
