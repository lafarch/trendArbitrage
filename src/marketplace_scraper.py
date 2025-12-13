"""
Phase 3: Marketplace Scraper Module
====================================
Purpose: Check product supply/saturation on e-commerce platforms

Why scrape marketplaces?
- Measure SUPPLY: how many sellers already offer this product
- Detect market saturation: 10,000 results = oversaturated
- Find opportunities: <50 results = underserved niche

Legal Note:
- This scrapes public data for research purposes
- Respect robots.txt and terms of service
- Use delays between requests
- Rotate user agents to avoid blocks
"""

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import logging
import re
from typing import Optional, Dict
from urllib.parse import urlencode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketplaceScraper:
    """
    Scrapes e-commerce platforms to count product availability.
    """
    
    def __init__(self, delay: int = 3, max_retries: int = 3):
        """
        Initialize scraper with anti-detection measures.
        
        Args:
            delay: Seconds to wait between requests (be respectful!)
            max_retries: Number of retry attempts on failure
        """
        self.delay = delay
        self.max_retries = max_retries
        self.ua = UserAgent()
        
        # Session for persistent connections
        self.session = requests.Session()
        
        logger.info("MarketplaceScraper initialized")
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Generate realistic browser headers to avoid detection.
        
        Why rotate user agents?
        - Websites block scrapers based on User-Agent strings
        - Rotating makes us look like different human users
        """
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def scrape_ebay(self, keyword: str) -> Optional[int]:
        """
        Scrape eBay to count total product listings for a keyword.
        
        Args:
            keyword: Search term (e.g., "clash royale plush")
            
        Returns:
            Total number of listings, or None if scraping failed
            
        How it works:
        1. Construct search URL with keyword
        2. Send GET request with realistic headers
        3. Parse HTML to find result count
        4. Extract number from text like "1,234 results for 'keyword'"
        """
        url = f"https://www.ebay.com/sch/i.html?_nkw={keyword.replace(' ', '+')}"
        
        for attempt in range(self.max_retries):
            try:
                # Send request
                response = self.session.get(
                    url,
                    headers=self._get_headers(),
                    timeout=10
                )
                
                # Check if successful
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Method 1: Look for result count in heading
                    # Example: "<h1>1,234 results for clash royale plush</h1>"
                    result_heading = soup.find('h1', class_='srp-controls__count-heading')
                    
                    if result_heading:
                        text = result_heading.get_text()
                        # Extract number using regex
                        # Matches patterns like "1,234" or "234" at start of string
                        match = re.search(r'([\d,]+)\s+results?', text)
                        if match:
                            count_str = match.group(1).replace(',', '')
                            count = int(count_str)
                            logger.info(f"eBay: Found {count} results for '{keyword}'")
                            time.sleep(self.delay)
                            return count
                    
                    # Method 2: Alternative selector
                    count_element = soup.select_one('.srp-controls__count')
                    if count_element:
                        text = count_element.get_text()
                        match = re.search(r'([\d,]+)', text)
                        if match:
                            count_str = match.group(1).replace(',', '')
                            count = int(count_str)
                            logger.info(f"eBay: Found {count} results for '{keyword}'")
                            time.sleep(self.delay)
                            return count
                    
                    # If no results found, assume 0
                    logger.warning(f"eBay: Could not parse result count for '{keyword}'")
                    return 0
                    
                elif response.status_code == 429:
                    # Rate limited - wait longer
                    logger.warning(f"eBay rate limit hit. Waiting 30 seconds...")
                    time.sleep(30)
                    
                else:
                    logger.warning(f"eBay returned status {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"eBay scraping error (attempt {attempt + 1}): {e}")
                time.sleep(self.delay * 2)  # Wait longer on error
        
        # All retries failed
        logger.error(f"Failed to scrape eBay for '{keyword}' after {self.max_retries} attempts")
        return None
    
    def scrape_amazon(self, keyword: str) -> Optional[int]:
        """
        Scrape Amazon to count total product listings.
        
        Args:
            keyword: Search term
            
        Returns:
            Total number of listings, or None if failed
            
        Note: Amazon is harder to scrape (CAPTCHAs, IP blocks)
        Consider using their official Product Advertising API for production
        """
        url = f"https://www.amazon.com/s?k={keyword.replace(' ', '+')}"
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(
                    url,
                    headers=self._get_headers(),
                    timeout=10
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Check for CAPTCHA
                    if 'captcha' in response.text.lower():
                        logger.error("Amazon CAPTCHA detected - use Selenium or API")
                        return None
                    
                    # Look for result count
                    # Example: "1-16 of over 1,000 results for"
                    result_text = soup.find('span', class_='a-color-state a-text-bold')
                    
                    if result_text:
                        text = result_text.get_text()
                        # Extract number after "of"
                        match = re.search(r'of\s+(?:over\s+)?([\d,]+)', text)
                        if match:
                            count_str = match.group(1).replace(',', '')
                            count = int(count_str)
                            logger.info(f"Amazon: Found {count} results for '{keyword}'")
                            time.sleep(self.delay)
                            return count
                    
                    # Count actual product divs as fallback
                    products = soup.find_all('div', {'data-component-type': 's-search-result'})
                    if products:
                        count = len(products)
                        logger.info(f"Amazon: Found ~{count} results (page 1 only) for '{keyword}'")
                        return count * 20  # Estimate: ~20 per page
                    
                    return 0
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Amazon scraping error: {e}")
                time.sleep(self.delay * 2)
        
        return None
    
    def get_supply_metrics(self, keyword: str, platforms: list = ['ebay']) -> Dict:
        """
        Get supply data from multiple platforms.
        
        Args:
            keyword: Product keyword to search
            platforms: List of platforms to check ('ebay', 'amazon')
            
        Returns:
            Dictionary with supply counts per platform
        """
        results = {'keyword': keyword}
        
        for platform in platforms:
            if platform.lower() == 'ebay':
                count = self.scrape_ebay(keyword)
                results['ebay_count'] = count if count is not None else -1
                
            elif platform.lower() == 'amazon':
                count = self.scrape_amazon(keyword)
                results['amazon_count'] = count if count is not None else -1
        
        # Calculate total supply
        counts = [v for k, v in results.items() if k.endswith('_count') and v >= 0]
        results['total_supply'] = sum(counts) if counts else -1
        
        return results


def demo():
    """Demo function to test the scraper."""
    scraper = MarketplaceScraper(delay=2)
    
    test_keywords = [
        "clash royale plush",
        "skibidi toilet toy",
        "digital circus plush"
    ]
    
    print("\n=== Testing eBay Scraper ===")
    for keyword in test_keywords:
        result = scraper.get_supply_metrics(keyword, platforms=['ebay'])
        print(f"{keyword}: {result}")


if __name__ == "__main__":
    demo()