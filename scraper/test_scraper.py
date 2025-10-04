#!/usr/bin/env python3
"""Test script to scrape just first 5 sections"""

import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://www.advocatekhoj.com/library/bareacts/bharatiyanyayasanhita"

# Test scraping first 5 sections
for i in range(1, 6):
    url = f"{BASE_URL}/{i}.php?Title=Bharatiya%20Nyaya%20Sanhita,%202023"
    print(f"\n{'='*60}")
    print(f"Section {i}")
    print(f"URL: {url}")
    print('='*60)

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Get all text
        text = soup.get_text(separator='\n', strip=True)

        # Print first 500 characters
        print(text[:800])

    except Exception as e:
        print(f"Error: {e}")
