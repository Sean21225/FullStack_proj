"""
Company Data API Service
Provides comprehensive company information using multiple free APIs
"""
import os
import requests
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class CompanyDataService:
    """
    Company data service using free APIs for comprehensive company information
    """
    
    def __init__(self):
        self.opencorporates_base = "https://api.opencorporates.com"
        self.fmp_base = "https://financialmodelingprep.com/api/v3"
        # FMP has a free tier - no API key needed for basic data
        
    def get_company_info(self, company_name: str) -> Dict[str, Any]:
        """
        Get comprehensive company information from multiple sources
        
        Args:
            company_name: Company name to search for
            
        Returns:
            Dict with company information
        """
        try:
            # First try to get basic company info from OpenCorporates
            company_info = self._search_opencorporates(company_name)
            
            # Try to enhance with financial data if it's a public company
            financial_data = self._search_fmp_by_name(company_name)
            
            # If no data from APIs, use web-based company lookup
            if not company_info and not financial_data:
                web_data = self._search_web_company_info(company_name)
                if web_data:
                    return web_data
            
            # Merge data from all sources
            result = self._merge_company_data(company_info, financial_data, company_name)
            
            return result
            
        except Exception as e:
            logger.error(f"Company data service error: {str(e)}")
            return self._fallback_company_info(company_name)
    
    def _search_opencorporates(self, company_name: str) -> Dict[str, Any]:
        """Search OpenCorporates for company information"""
        try:
            url = f"{self.opencorporates_base}/companies/search"
            params = {
                "q": company_name,
                "format": "json",
                "per_page": 5
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            companies = data.get("results", {}).get("companies", [])
            
            if companies:
                # Find best match (exact or closest match)
                best_match = None
                company_name_lower = company_name.lower()
                
                for company_data in companies:
                    company = company_data.get("company", {})
                    name = company.get("name", "").lower()
                    
                    # Exact match gets priority
                    if company_name_lower in name or name in company_name_lower:
                        best_match = company
                        break
                
                if not best_match and companies:
                    best_match = companies[0].get("company", {})
                
                if best_match:
                    return {
                        "name": best_match.get("name", company_name),
                        "jurisdiction": best_match.get("jurisdiction_code"),
                        "company_type": best_match.get("company_type"),
                        "status": best_match.get("current_status"),
                        "address": best_match.get("registered_address_in_full"),
                        "incorporation_date": best_match.get("incorporation_date"),
                        "source": "opencorporates"
                    }
            
            return {}
            
        except Exception as e:
            logger.warning(f"OpenCorporates search failed: {str(e)}")
            return {}
    
    def _search_fmp_by_name(self, company_name: str) -> Dict[str, Any]:
        """Search Financial Modeling Prep for public company data"""
        try:
            # First, search for company symbol
            search_url = f"{self.fmp_base}/search"
            params = {"query": company_name, "limit": 10}
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            search_results = response.json()
            
            if search_results:
                # Find best match
                company_name_lower = company_name.lower()
                best_symbol = None
                
                for result in search_results:
                    name = result.get("name", "").lower()
                    if company_name_lower in name or name in company_name_lower:
                        best_symbol = result.get("symbol")
                        break
                
                if not best_symbol and search_results:
                    best_symbol = search_results[0].get("symbol")
                
                if best_symbol:
                    # Get detailed company profile
                    profile_url = f"{self.fmp_base}/profile/{best_symbol}"
                    profile_response = requests.get(profile_url, timeout=10)
                    profile_response.raise_for_status()
                    
                    profile_data = profile_response.json()
                    
                    if profile_data and len(profile_data) > 0:
                        company = profile_data[0]
                        return {
                            "name": company.get("companyName"),
                            "symbol": company.get("symbol"),
                            "industry": company.get("industry"),
                            "sector": company.get("sector"),
                            "website": company.get("website"),
                            "description": company.get("description"),
                            "ceo": company.get("ceo"),
                            "employees": company.get("fullTimeEmployees"),
                            "headquarters": f"{company.get('city', '')}, {company.get('state', '')}, {company.get('country', '')}".strip(", "),
                            "market_cap": company.get("mktCap"),
                            "source": "fmp"
                        }
            
            return {}
            
        except Exception as e:
            logger.warning(f"FMP search failed: {str(e)}")
            return {}
    
    def _merge_company_data(self, opencorp_data: Dict, fmp_data: Dict, company_name: str) -> Dict[str, Any]:
        """Merge data from multiple sources into comprehensive company info"""
        
        # Start with the most complete dataset
        if fmp_data and fmp_data.get("name"):
            primary_data = fmp_data
            secondary_data = opencorp_data
        elif opencorp_data and opencorp_data.get("name"):
            primary_data = opencorp_data
            secondary_data = fmp_data
        else:
            return self._fallback_company_info(company_name)
        
        # Build comprehensive company information
        result = {
            "name": primary_data.get("name", company_name),
            "industry": (
                fmp_data.get("industry") or 
                self._map_company_type_to_industry(opencorp_data.get("company_type", "")) or
                "Technology"
            ),
            "size": self._determine_company_size(fmp_data, opencorp_data),
            "description": (
                fmp_data.get("description") or
                f"Registered company in {opencorp_data.get('jurisdiction', 'multiple jurisdictions')}" or
                f"Established company with global presence"
            ),
            "website": fmp_data.get("website"),
            "headquarters": (
                fmp_data.get("headquarters") or
                opencorp_data.get("address") or
                "Multiple locations"
            ),
            "ceo": fmp_data.get("ceo"),
            "market_cap": fmp_data.get("market_cap"),
            "symbol": fmp_data.get("symbol"),
            "sector": fmp_data.get("sector"),
            "status": opencorp_data.get("status"),
            "incorporation_date": opencorp_data.get("incorporation_date")
        }
        
        # Clean up None values
        return {k: v for k, v in result.items() if v is not None}
    
    def _determine_company_size(self, fmp_data: Dict, opencorp_data: Dict) -> str:
        """Determine company size description"""
        
        employees = fmp_data.get("employees")
        if employees:
            if employees >= 10000:
                return f"Large Enterprise ({employees:,} employees)"
            elif employees >= 1000:
                return f"Large Company ({employees:,} employees)"
            elif employees >= 100:
                return f"Medium Company ({employees:,} employees)"
            else:
                return f"Small Company ({employees:,} employees)"
        
        market_cap = fmp_data.get("market_cap")
        if market_cap:
            if market_cap >= 200000000000:  # $200B+
                return "Mega Cap Company"
            elif market_cap >= 10000000000:  # $10B+
                return "Large Cap Company"
            elif market_cap >= 2000000000:   # $2B+
                return "Mid Cap Company"
            else:
                return "Small Cap Company"
        
        # Fallback based on company type or status
        company_type = opencorp_data.get("company_type", "").lower()
        if "public" in company_type or "plc" in company_type:
            return "Public Company"
        elif "private" in company_type or "ltd" in company_type:
            return "Private Company"
        
        return "Established Company"
    
    def _map_company_type_to_industry(self, company_type: Optional[str]) -> Optional[str]:
        """Map legal company type to industry category"""
        if not company_type:
            return None
            
        company_type = company_type.lower()
        
        # Basic mapping - can be expanded
        if any(term in company_type for term in ["tech", "software", "digital"]):
            return "Technology"
        elif any(term in company_type for term in ["bank", "financial", "investment"]):
            return "Financial Services"
        elif any(term in company_type for term in ["retail", "commerce", "trade"]):
            return "Retail"
        elif any(term in company_type for term in ["manufacturing", "industrial"]):
            return "Manufacturing"
        
        return None
    
    def _search_web_company_info(self, company_name: str) -> Dict[str, Any]:
        """Search for company information using known company database"""
        
        # Known company information database (can be expanded)
        company_database = {
            "google": {
                "name": "Google LLC",
                "industry": "Technology",
                "sector": "Internet Services",
                "size": "Large Enterprise (180,000+ employees)",
                "description": "Multinational technology company specializing in Internet-related services and products, including online advertising, search engine, cloud computing, software, and hardware.",
                "website": "https://www.google.com",
                "headquarters": "Mountain View, California, United States",
                "ceo": "Sundar Pichai"
            },
            "apple": {
                "name": "Apple Inc.",
                "industry": "Technology",
                "sector": "Consumer Electronics",
                "size": "Large Enterprise (164,000+ employees)",
                "description": "American multinational technology company that designs, develops, and sells consumer electronics, computer software, and online services.",
                "website": "https://www.apple.com",
                "headquarters": "Cupertino, California, United States",
                "ceo": "Tim Cook"
            },
            "microsoft": {
                "name": "Microsoft Corporation",
                "industry": "Technology",
                "sector": "Software",
                "size": "Large Enterprise (221,000+ employees)",
                "description": "American multinational technology corporation that produces computer software, consumer electronics, personal computers, and related services.",
                "website": "https://www.microsoft.com",
                "headquarters": "Redmond, Washington, United States",
                "ceo": "Satya Nadella"
            },
            "amazon": {
                "name": "Amazon.com Inc.",
                "industry": "Technology/E-commerce",
                "sector": "Online Retail",
                "size": "Large Enterprise (1,500,000+ employees)",
                "description": "American multinational technology company focusing on e-commerce, cloud computing, digital streaming, and artificial intelligence.",
                "website": "https://www.amazon.com",
                "headquarters": "Seattle, Washington, United States",
                "ceo": "Andy Jassy"
            },
            "facebook": {
                "name": "Meta Platforms Inc.",
                "industry": "Technology",
                "sector": "Social Media",
                "size": "Large Enterprise (86,000+ employees)",
                "description": "American multinational technology conglomerate holding company focused on social technology and metaverse development.",
                "website": "https://about.meta.com",
                "headquarters": "Menlo Park, California, United States",
                "ceo": "Mark Zuckerberg"
            },
            "meta": {
                "name": "Meta Platforms Inc.",
                "industry": "Technology",
                "sector": "Social Media",
                "size": "Large Enterprise (86,000+ employees)",
                "description": "American multinational technology conglomerate holding company focused on social technology and metaverse development.",
                "website": "https://about.meta.com",
                "headquarters": "Menlo Park, California, United States",
                "ceo": "Mark Zuckerberg"
            },
            "netflix": {
                "name": "Netflix Inc.",
                "industry": "Entertainment",
                "sector": "Streaming Media",
                "size": "Large Company (12,800+ employees)",
                "description": "American streaming entertainment service and production company offering TV series, documentaries and feature films across a wide variety of genres and languages.",
                "website": "https://www.netflix.com",
                "headquarters": "Los Gatos, California, United States",
                "ceo": "Ted Sarandos"
            },
            "tesla": {
                "name": "Tesla Inc.",
                "industry": "Automotive",
                "sector": "Electric Vehicles",
                "size": "Large Company (127,000+ employees)",
                "description": "American multinational automotive and clean energy company designing and manufacturing electric vehicles, battery energy storage, solar panels and related products.",
                "website": "https://www.tesla.com",
                "headquarters": "Austin, Texas, United States",
                "ceo": "Elon Musk"
            },
            "nvidia": {
                "name": "NVIDIA Corporation",
                "industry": "Technology",
                "sector": "Semiconductors",
                "size": "Large Company (29,600+ employees)",
                "description": "American multinational technology company incorporated in Delaware and based in California, designing graphics processing units (GPUs) for gaming and professional markets, as well as system on a chip units (SoCs) for mobile computing and automotive markets.",
                "website": "https://www.nvidia.com",
                "headquarters": "Santa Clara, California, United States",
                "ceo": "Jensen Huang"
            },
            "salesforce": {
                "name": "Salesforce Inc.",
                "industry": "Technology",
                "sector": "Cloud Computing",
                "size": "Large Company (73,000+ employees)",
                "description": "American cloud-based software company headquartered in San Francisco, California. It provides customer relationship management (CRM) software and applications focused on sales, customer service, marketing automation, analytics, and application development.",
                "website": "https://www.salesforce.com",
                "headquarters": "San Francisco, California, United States",
                "ceo": "Marc Benioff"
            }
        }
        
        # Search for company (case-insensitive)
        company_key = company_name.lower().strip()
        
        # Direct match
        if company_key in company_database:
            return company_database[company_key]
            
        # Partial match
        for key, data in company_database.items():
            if company_key in key or key in company_key:
                return data
                
        # Check if company name is in the full company name
        for key, data in company_database.items():
            full_name = data["name"].lower()
            if company_key in full_name or any(word in full_name for word in company_key.split()):
                return data
        
        return {}

    def _fallback_company_info(self, company_name: str) -> Dict[str, Any]:
        """Fallback company information when no data is found"""
        return {
            "name": company_name,
            "industry": "Information not available",
            "size": "Company size not disclosed",
            "description": f"We couldn't find detailed information for {company_name}. This may be a private company or the information is not publicly available.",
            "website": None,
            "headquarters": "Location not disclosed"
        }