"""
Phase 3: Marketplace Scraper Module (Fixed Version)
====================================================
Purpose: Check product supply/saturation on e-commerce platforms

FIXES:
- Increased timeout from 10s to 30s
- Better error handling for timeouts
- More aggressive delays between requests
- Fallback to eBay-only if Amazon is blocking
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

    def __init__(self, delay: int = 5, max_retries: int = 2):
        """
        Initialize scraper with anti-detection measures.

        Args:
            delay: Seconds to wait between requests (increased to 5)
            max_retries: Number of retry attempts on failure (reduced to 2)
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
        """
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        }

    def scrape_ebay(self, keyword: str) -> Optional[int]:
        """
        Scrape eBay search results count.
        """
        url = f"https://www.ebay.com/sch/i.html?_nkw={keyword.replace(' ', '+')}"

        for attempt in range(self.max_retries):
            try:
                response = self.session.get(
                    url, 
                    headers=self._get_headers(), 
                    timeout=30  # Increased from 10 to 30 seconds
                )

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "html.parser")
                    page_text = soup.get_text()

                    # Search for result count
                    match = re.search(
                        r"([\d,]+)\+?\s+(?:results|resultados)",
                        page_text,
                        re.IGNORECASE,
                    )

                    if match:
                        count_str = match.group(1).replace(",", "")
                        count = int(count_str)
                        logger.info(f"eBay: Found {count} items for '{keyword}'")
                        time.sleep(self.delay)
                        return count

                    # Fallback: look for "No exact matches found"
                    if "no exact matches found" in page_text.lower():
                        logger.info(f"eBay: 0 items for '{keyword}' (no matches)")
                        return 0

                    logger.warning(f"eBay: Could not find count for '{keyword}'")

                elif response.status_code == 429:
                    logger.warning(f"eBay rate limit hit. Waiting 20s...")
                    time.sleep(20)

            except requests.exceptions.Timeout:
                logger.error(f"eBay timeout for '{keyword}' (attempt {attempt+1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(10)
                    
            except Exception as e:
                logger.error(f"Error scraping eBay: {e}")

        return 0

    def scrape_amazon(self, keyword: str) -> Optional[int]:
        """
        Scrape Amazon search results count.
        NOTE: Amazon aggressively blocks scrapers. This may often fail.
        """
        domain = "amazon.com"
        url = f"https://www.{domain}/s?k={keyword.replace(' ', '+')}"

        for attempt in range(self.max_retries):
            try:
                headers = {
                    "User-Agent": self.ua.random,
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://www.google.com/",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                }

                response = self.session.get(
                    url, 
                    headers=headers, 
                    timeout=30  # Increased from 10 to 30
                )

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "html.parser")
                    page_text = soup.get_text()

                    # Search for result count
                    match = re.search(
                        r"(?:of|de)\s+(?:over|más de)?\s*([\d,.]+)\s+(?:results|resultados)",
                        page_text,
                        re.IGNORECASE,
                    )

                    if match:
                        count_str = match.group(1).replace(",", "").replace(".", "")
                        count = int(count_str)
                        logger.info(f"Amazon: Found {count} items for '{keyword}'")
                        time.sleep(self.delay)
                        return count

                    # Fallback regex
                    match_simple = re.search(
                        r"([\d,.]+)\s+(?:results|resultados)", 
                        page_text, 
                        re.IGNORECASE
                    )
                    if match_simple:
                        count_str = match_simple.group(1).replace(",", "").replace(".", "")
                        return int(count_str)

                    logger.warning(f"Amazon: Could not parse count for '{keyword}' (likely CAPTCHA)")

                elif response.status_code == 503:
                    logger.warning("Amazon 503 (Bot detected or server busy)")
                    # Don't retry on 503 - it's a hard block
                    break

            except requests.exceptions.Timeout:
                logger.error(f"Amazon timeout for '{keyword}'")
                
            except Exception as e:
                logger.error(f"Error scraping Amazon: {e}")

            # Wait longer between Amazon retries
            if attempt < self.max_retries - 1:
                time.sleep(15)

        return -1  # Return -1 to indicate failure (not 0, which could mean no results)

    def get_supply_metrics(self, keyword: str, platforms: list = ["ebay"]) -> Dict:
        """
        Get supply data from multiple platforms.

        Args:
            keyword: Product keyword to search
            platforms: List of platforms to check ('ebay', 'amazon')

        Returns:
            Dictionary with supply counts per platform
        """
        results = {"keyword": keyword}

        for platform in platforms:
            if platform.lower() == "ebay":
                count = self.scrape_ebay(keyword)
                results["ebay_count"] = count if count is not None else 0

            elif platform.lower() == "amazon":
                count = self.scrape_amazon(keyword)
                # Only include Amazon if we got real data (not -1 = failed)
                if count >= 0:
                    results["amazon_count"] = count
                else:
                    results["amazon_count"] = -1  # Mark as failed
                    logger.warning(f"Amazon scraping failed for '{keyword}', using eBay only")

        # Calculate total supply (exclude failed Amazon attempts)
        counts = [v for k, v in results.items() if k.endswith("_count") and v >= 0]
        results["total_supply"] = sum(counts) if counts else 0

        return results


def demo():
    """Demo function to test the scraper."""
    scraper = MarketplaceScraper(delay=5)

    test_keywords = ["pokemon plush"]

    print("\n=== Testing eBay Scraper ===")
    for keyword in test_keywords:
        result = scraper.get_supply_metrics(keyword, platforms=["ebay"])
        print(f"{keyword}: {result}")


if __name__ == "__main__":
    demo()