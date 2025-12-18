"""
Phase 3: Marketplace Scraper Module (SerpAPI Version)
====================================================
Purpose: Check product supply/saturation on e-commerce platforms

Platforms supported:
- Amazon
- eBay
- Walmart
- AliExpress

Uses SerpAPI for ~98% reliability (no bot detection).
"""

import time
import logging
from typing import Dict, List
import os
from dotenv import load_dotenv

from serpapi.google_search import GoogleSearch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class MarketplaceScraper:
    """
    Retrieves product supply counts using SerpAPI marketplace engines.
    """

    def __init__(self, delay: int = 3, max_retries: int = 3):
        self.delay = delay
        self.max_retries = max_retries
        self.api_key = os.getenv("SERPAPI_KEY")

        if not self.api_key:
            raise ValueError("❌ SERPAPI_API_KEY not found in environment")

        logger.info("MarketplaceScraper initialized (SerpAPI mode)")

    # -------------------------
    # Generic SerpAPI fetcher
    # -------------------------
    def _query_serpapi(self, params: Dict) -> int:
        """
        Query SerpAPI and extract total results safely.
        """
        params["api_key"] = self.api_key

        for attempt in range(self.max_retries):
            try:
                search = GoogleSearch(params)
                results = search.get_dict()

                count = (
                    results.get("search_information", {})
                    .get("total_results")
                )

                if count is not None:
                    return int(count)

            except Exception as e:
                logger.warning(f"SerpAPI error (attempt {attempt+1}): {e}")
                time.sleep(self.delay)

        return -1  # failed after retries

    # -------------------------
    # Platform-specific methods
    # -------------------------
    def amazon_supply(self, keyword: str) -> int:
        return self._query_serpapi({
            "engine": "amazon",
            "amazon_domain": "amazon.com",
            "k": keyword,
        })

    def ebay_supply(self, keyword: str) -> int:
        return self._query_serpapi({
            "engine": "ebay",
            "_nkw": keyword,
        })

    def walmart_supply(self, keyword: str) -> int:
        return self._query_serpapi({
            "engine": "walmart",
            "query": keyword,
        })

    def aliexpress_supply(self, keyword: str) -> int:
        return self._query_serpapi({
            "engine": "aliexpress",
            "query": keyword,
        })

    # -------------------------
    # Public interface (USED BY main.py)
    # -------------------------
    def get_supply_metrics(
        self,
        keyword: str,
        platforms: List[str] = ["amazon", "ebay"],
    ) -> Dict:
        """
        Get supply counts across selected platforms.
        """
        results = {"keyword": keyword}

        platform_map = {
            "amazon": self.amazon_supply,
            "ebay": self.ebay_supply,
            "walmart": self.walmart_supply,
            "aliexpress": self.aliexpress_supply,
        }

        total_supply = 0

        for platform in platforms:
            func = platform_map.get(platform.lower())
            if not func:
                continue

            count = func(keyword)
            results[f"{platform}_count"] = count

            if count >= 0:
                total_supply += count

            logger.info(f"{platform.capitalize()}: {count} results for '{keyword}'")
            time.sleep(self.delay)

        results["total_supply"] = total_supply
        return results
