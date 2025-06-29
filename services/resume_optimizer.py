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
        elif word_count < 50:
            score += 5  # Very short content gets low score
        else:
            score += 10
        
        # Action verbs presence (25% of score)
        action_verb_count = sum(1 for verb in self.action_verbs if verb.lower() in resume_content.lower())
        score += min(25, action_verb_count * 2)  # Reduced multiplier
        
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
            elif any(word in job_lower for word in ["marketing", "seo", "social"]):
                field_keywords = self.tech_keywords["marketing"]
            
            if field_keywords:
                matching_keywords = sum(1 for keyword in field_keywords if keyword.lower() in resume_lower)
                score += min(25, matching_keywords * 1.5)  # Reduced multiplier
            else:
                score += 8  # Base score if no specific field detected
        else:
            score += 8
        
        # Format and structure (20% of score)
        sections = ["experience", "education", "skills", "summary", "objective"]
        section_count = sum(1 for section in sections if section in resume_content.lower())
        score += min(20, section_count * 3)  # Reduced multiplier
        
        # Ensure score is always between 5 and 100
        final_score = max(5.0, min(100.0, score))
        return round(final_score, 1)
    
    def _generate_suggestions(self, resume_content: str, job_description: Optional[str] = None) -> List[str]:
        """Generate intelligent suggestions for resume improvement"""
        suggestions = []
        word_count = len(resume_content.split())
        
        # Handle very short content differently
        if word_count < 20:
            suggestions = [
                "Your resume is very brief. Consider expanding with specific experience and accomplishments",
                "Add a professional summary highlighting your strengths and career goals",
                "Include specific technical skills, tools, or programming languages you know",
                "Add any relevant education, certifications, or training",
                "Include measurable achievements from work, projects, or studies",
                "Structure your resume with clear sections (Summary, Skills, Experience, Education)"
            ]
            return suggestions
        
        # Check for weak words
        for weak, strong in self.weak_words.items():
            if weak in resume_content.lower():
                suggestions.append(f"Replace '{weak}' with '{strong}' for stronger impact")
        
        # Check for action verbs
        action_verb_count = sum(1 for verb in self.action_verbs if verb.lower() in resume_content.lower())
        if action_verb_count < 3:
            suggestions.append("Use more action verbs like 'Developed', 'Implemented', 'Led' to strengthen accomplishments")
        
        # Check length
        if word_count < 300:
            suggestions.append("Expand your resume with specific accomplishments, skills, and relevant experience")
        elif word_count > 800:
            suggestions.append("Consider condensing your resume to focus on the most relevant achievements")
        
        # Check for quantified achievements
        if not re.search(r'\d+%|\$\d+|\d+\s+(years?|months?|projects?|users?|clients?)', resume_content):
            suggestions.append("Add quantified achievements (e.g., 'Increased efficiency by 25%', 'Completed 10+ projects')")
        
        # Job-specific suggestions based on description
        if job_description:
            job_lower = job_description.lower()
            resume_lower = resume_content.lower()
            
            if "python" in job_lower and "python" not in resume_lower:
                suggestions.append("Highlight Python programming experience if you have it")
            if "javascript" in job_lower and "javascript" not in resume_lower:
                suggestions.append("Mention JavaScript skills if relevant to your background")
            if "teamwork" in job_lower and not any(word in resume_lower for word in ["team", "collaborate", "group"]):
                suggestions.append("Emphasize teamwork and collaboration experience")
        
        # Structure suggestions
        if "summary" not in resume_content.lower() and "objective" not in resume_content.lower():
            suggestions.append("Add a professional summary at the top highlighting your key strengths")
        
        return suggestions[:6]  # Limit to most actionable suggestions
    
    def _optimize_content(self, resume_content: str, job_description: Optional[str] = None) -> str:
        """Apply automatic optimizations to resume content"""
        optimized = resume_content.strip()
        
        # For very short content, provide a more structured version
        if len(optimized.split()) < 20:
            optimized = self._expand_short_content(optimized, job_description)
        
        # Replace weak words with stronger alternatives
        for weak, strong in self.weak_words.items():
            pattern = re.compile(re.escape(weak), re.IGNORECASE)
            optimized = pattern.sub(strong, optimized)
        
        # Improve bullet point formatting
        lines = optimized.split('\n')
        improved_lines = []
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                improved_lines.append(line)
                continue
                
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
    
    def _expand_short_content(self, content: str, job_description: Optional[str] = None) -> str:
        """Expand very short resume content with suggested structure"""
        content_lower = content.lower()
        original_content = content.strip()
        
        # Detect if it's about programming/software
        if any(word in content_lower for word in ["program", "code", "software", "develop", "coding"]):
            # Make it sound more natural and less template-like
            programming_level = "beginner" if any(word in content_lower for word in ["little", "bit", "new", "learning"]) else "developing"
            
            return f"""PROFESSIONAL SUMMARY
Entry-level software developer with foundational programming skills and enthusiasm for technology. Currently building technical expertise and seeking opportunities to apply programming knowledge in real-world projects.

TECHNICAL SKILLS
• Programming Experience: {original_content}
• Problem-solving and logical thinking
• Self-directed learning and research
• Basic understanding of software development concepts

PROJECTS & EXPERIENCE  
• Practicing programming fundamentals through personal study
• Working on small coding exercises and tutorials
• Developing problem-solving skills through programming challenges
• Building foundation in software development best practices

EDUCATION & LEARNING
• Actively learning programming languages and development tools
• Committed to continuous improvement in technical skills
• Studying software development concepts and methodologies"""
        
        # Generic professional expansion
        # Clean up the content for better presentation
        cleaned_content = original_content.replace('\n', ' ').strip()
        content_words = cleaned_content.split()
        
        # Create a more professional summary based on content
        if len(content_words) > 3:
            main_interest = ' '.join(content_words[:4])
            skills_focus = ' '.join(content_words[4:]) if len(content_words) > 4 else "professional development"
        else:
            main_interest = cleaned_content
            skills_focus = "professional growth"
        
        return f"""PROFESSIONAL SUMMARY
Motivated professional with experience in {main_interest} and commitment to {skills_focus}. Demonstrates strong work ethic and dedication to continuous learning and professional excellence.

CORE STRENGTHS
• {main_interest.title()}
• Strong communication and interpersonal skills
• Problem-solving and analytical thinking
• Adaptable and eager to take on new challenges

EXPERIENCE & BACKGROUND
• Applied skills in {main_interest} through various projects and situations
• Demonstrated reliability and attention to detail in work
• Actively seeking opportunities to expand professional capabilities
• Committed to delivering quality results and continuous improvement

PROFESSIONAL DEVELOPMENT
• Self-motivated learner with genuine interest in {skills_focus}
• Open to feedback and dedicated to skill enhancement
• Strong work ethic and positive attitude toward challenges"""
    
    def optimize_resume(self, request: ResumeOptimizationRequest) -> ResumeOptimizationResponse:
        """
        Optimize resume content using free rule-based analysis
        Returns optimized content with intelligent suggestions and scoring
        """
        try:
            # Calculate quality score based on ORIGINAL content
            score = self._calculate_score(request.resume_content, request.job_description)
            
            # Generate improvement suggestions based on original content
            suggestions = self._generate_suggestions(request.resume_content, request.job_description)
            
            # Apply content optimizations (this may expand short content)
            optimized_content = self._optimize_content(request.resume_content, request.job_description)
            
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
                score=25.0
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
