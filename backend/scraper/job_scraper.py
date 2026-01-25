"""
Job market scraper using multiple sources. 
Prioritizes APIs over scraping for reliability and legality.
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import aiohttp
from bs4 import BeautifulSoup

from backend.db.pg import get_conn


@dataclass
class JobListing:
    title: str
    company: str
    location: str
    salary_min: Optional[float]
    salary_max: Optional[float]
    description: str
    url: str
    source: str
    posted_date: Optional[datetime]
    skills_required: List[str]


class JobMarketScraper: 
    """
    Aggregates job market data from multiple sources. 
    Uses APIs where available, falls back to scraping public sites.
    """
    
    def __init__(self):
        self.serpapi_key = os.getenv("SERPAPI_KEY")  # For Google Jobs
        self.adzuna_app_id = os. getenv("ADZUNA_APP_ID")
        self.adzuna_api_key = os.getenv("ADZUNA_API_KEY")
        self.cache_duration = timedelta(hours=6)
        self._cache:  Dict[str, Any] = {}
    
    async def search_jobs(
        self,
        query: str,
        location: str = "United States",
        limit: int = 20
    ) -> List[JobListing]: 
        """
        Search for jobs across multiple sources.
        
        Args:
            query: Job title or keywords (e.g., "Machine Learning Engineer")
            location: Location to search (e.g., "San Francisco, CA")
            limit: Maximum results to return
            
        Returns: 
            List of JobListing objects
        """
        cache_key = f"{query}:{location}:{limit}"
        
        # Check cache
        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                return cached_data
        
        # Gather from multiple sources in parallel
        tasks = []
        
        if self. adzuna_app_id and self.adzuna_api_key: 
            tasks.append(self._search_adzuna(query, location, limit))
        
        if self.serpapi_key:
            tasks.append(self._search_google_jobs(query, location, limit))
        
        # Always include free sources
        tasks.append(self._search_remoteok(query, limit))
        
        results = await asyncio. gather(*tasks, return_exceptions=True)
        
        # Flatten and deduplicate results
        all_jobs = []
        seen_urls = set()
        
        for result in results:
            if isinstance(result, Exception):
                print(f"Scraper error: {result}")
                continue
            for job in result: 
                if job.url not in seen_urls:
                    seen_urls.add(job.url)
                    all_jobs.append(job)
        
        # Sort by posted date (newest first)
        all_jobs.sort(
            key=lambda j: j.posted_date or datetime.min,
            reverse=True
        )
        
        # Cache and return
        final_results = all_jobs[:limit]
        self._cache[cache_key] = (datetime.now(), final_results)
        
        return final_results
    
    async def _search_adzuna(
        self,
        query: str,
        location: str,
        limit: int
    ) -> List[JobListing]: 
        """Search Adzuna API (free tier:  250 requests/month)."""
        
        # Map location to country code
        country = "us"  # Default to US
        if "uk" in location.lower() or "united kingdom" in location. lower():
            country = "gb"
        elif "canada" in location.lower():
            country = "ca"
        
        url = f"https://api.adzuna. com/v1/api/jobs/{country}/search/1"
        params = {
            "app_id": self. adzuna_app_id,
            "app_key": self. adzuna_api_key,
            "what": query,
            "where": location,
            "results_per_page": limit,
            "content-type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response. status != 200:
                    return []
                
                data = await response. json()
                jobs = []
                
                for result in data.get("results", []):
                    jobs.append(JobListing(
                        title=result.get("title", ""),
                        company=result.get("company", {}).get("display_name", "Unknown"),
                        location=result.get("location", {}).get("display_name", location),
                        salary_min=result. get("salary_min"),
                        salary_max=result. get("salary_max"),
                        description=result.get("description", "")[: 500],
                        url=result.get("redirect_url", ""),
                        source="adzuna",
                        posted_date=datetime.fromisoformat(
                            result.get("created", "")[:19]
                        ) if result.get("created") else None,
                        skills_required=[]
                    ))
                
                return jobs
    
    async def _search_google_jobs(
        self,
        query: str,
        location: str,
        limit: int
    ) -> List[JobListing]: 
        """Search Google Jobs via SerpAPI."""
        
        url = "https://serpapi.com/search.json"
        params = {
            "engine": "google_jobs",
            "q": query,
            "location": location,
            "api_key": self. serpapi_key,
            "num": limit
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                jobs = []
                
                for result in data.get("jobs_results", []):
                    # Extract salary if available
                    salary_min = None
                    salary_max = None
                    
                    if "salary" in result: 
                        # Parse salary string like "$80K - $120K"
                        salary_str = result. get("salary", "")
                        # Basic parsing - could be improved
                        import re
                        numbers = re.findall(r'\d+', salary_str. replace(',', ''))
                        if len(numbers) >= 2:
                            salary_min = float(numbers[0]) * 1000
                            salary_max = float(numbers[1]) * 1000
                    
                    jobs.append(JobListing(
                        title=result.get("title", ""),
                        company=result.get("company_name", "Unknown"),
                        location=result.get("location", location),
                        salary_min=salary_min,
                        salary_max=salary_max,
                        description=result. get("description", "")[:500],
                        url=result. get("apply_link", result.get("share_link", "")),
                        source="google_jobs",
                        posted_date=None,  # Google Jobs doesn't give exact dates
                        skills_required=result.get("detected_extensions", {}).get(
                            "skills", []
                        )
                    ))
                
                return jobs
    
    async def _search_remoteok(
        self,
        query: str,
        limit: int
    ) -> List[JobListing]: 
        """
        Search RemoteOK (free, no API key needed).
        Only returns remote jobs. 
        """
        
        url = f"https://remoteok.com/api? tag={query. replace(' ', '-').lower()}"
        
        async with aiohttp.ClientSession() as session:
            headers = {"User-Agent": "CareerCompass/1.0"}
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                jobs = []
                
                # First item is metadata, skip it
                for result in data[1:limit+1]:
                    # Parse salary
                    salary_min = None
                    salary_max = None
                    if result.get("salary_min"):
                        salary_min = float(result["salary_min"])
                    if result.get("salary_max"):
                        salary_max = float(result["salary_max"])
                    
                    jobs.append(JobListing(
                        title=result. get("position", ""),
                        company=result. get("company", "Unknown"),
                        location="Remote",
                        salary_min=salary_min,
                        salary_max=salary_max,
                        description=result.get("description", "")[:500],
                        url=result.get("url", ""),
                        source="remoteok",
                        posted_date=datetime.fromtimestamp(
                            result.get("epoch", 0)
                        ) if result.get("epoch") else None,
                        skills_required=result.get("tags", [])
                    ))
                
                return jobs
    
    async def get_market_insights(
        self,
        job_title: str,
        location: str = "United States"
    ) -> Dict[str, Any]: 
        """
        Get aggregated market insights for a job title.
        Useful for the recommender agent.
        """
        
        jobs = await self.search_jobs(job_title, location, limit=50)
        
        if not jobs: 
            return {
                "job_title": job_title,
                "location": location,
                "jobs_found": 0,
                "insights":  None
            }
        
        # Calculate salary statistics
        salaries_min = [j.salary_min for j in jobs if j.salary_min]
        salaries_max = [j. salary_max for j in jobs if j. salary_max]
        
        avg_salary_min = sum(salaries_min) / len(salaries_min) if salaries_min else None
        avg_salary_max = sum(salaries_max) / len(salaries_max) if salaries_max else None
        
        # Extract common skills
        all_skills = []
        for job in jobs:
            all_skills.extend(job.skills_required)
        
        skill_counts = {}
        for skill in all_skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        top_skills = sorted(
            skill_counts.items(),
            key=lambda x:  x[1],
            reverse=True
        )[:10]
        
        # Get top companies hiring
        company_counts = {}
        for job in jobs: 
            company_counts[job.company] = company_counts.get(job. company, 0) + 1
        
        top_companies = sorted(
            company_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "job_title": job_title,
            "location":  location,
            "jobs_found": len(jobs),
            "insights": {
                "salary_range": {
                    "min": avg_salary_min,
                    "max":  avg_salary_max,
                    "currency": "USD"
                },
                "in_demand_skills": [
                    {"skill": skill, "mentions": count}
                    for skill, count in top_skills
                ],
                "top_hiring_companies": [
                    {"company":  company, "openings": count}
                    for company, count in top_companies
                ],
                "remote_percentage": len([j for j in jobs if "remote" in j.location.lower()]) / len(jobs) * 100,
                "sources_used": list(set(j.source for j in jobs))
            }
        }