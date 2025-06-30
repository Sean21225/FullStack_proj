#!/usr/bin/env python3
"""Test script for Adzuna API integration"""

import os
import sys
sys.path.append('.')

from services.google_jobs_api import adzuna_jobs_service

def test_adzuna():
    print("Testing Adzuna API integration...")
    print(f"App ID: {adzuna_jobs_service.app_id}")
    print(f"App Key: {adzuna_jobs_service.app_key[:10]}...")
    
    # Test Tel Aviv search
    print("\n--- Testing Tel Aviv search ---")
    tel_aviv_jobs = adzuna_jobs_service.search_jobs(
        query="software",
        location="tel aviv",
        limit=3
    )
    
    print(f"Found {len(tel_aviv_jobs)} jobs in Tel Aviv")
    for job in tel_aviv_jobs:
        print(f"- {job['title']} at {job['company']} in {job['location']}")
    
    # Test Washington search
    print("\n--- Testing Washington search ---")
    washington_jobs = adzuna_jobs_service.search_jobs(
        query="software",
        location="washington",
        limit=3
    )
    
    print(f"Found {len(washington_jobs)} jobs in Washington")
    for job in washington_jobs:
        print(f"- {job['title']} at {job['company']} in {job['location']}")

if __name__ == "__main__":
    test_adzuna()