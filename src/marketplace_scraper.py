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
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def scrape_ebay(self, keyword: str) -> Optional[int]:
        """
        Versión Robusta: Busca el texto 'resultados' en cualquier parte de la página.
        """
        url = f"https://www.ebay.com/sch/i.html?_nkw={keyword.replace(' ', '+')}"

        for attempt in range(self.max_retries):
            try:
                response = self.session.get(
                    url, headers=self._get_headers(), timeout=10
                )

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "html.parser")

                    # ESTRATEGIA: Buscar el texto directamente en el código fuente
                    page_text = soup.get_text()

                    # Regex poderosa: Busca un número seguido de "result..." o "resultado..."
                    # Ejemplos que detecta: "72 resultados", "1,000 results", "50+ resultados"
                    match = re.search(
                        r"([\d,]+)\+?\s+(?:results|resultados)",
                        page_text,
                        re.IGNORECASE,
                    )

                    if match:
                        count_str = match.group(1).replace(",", "")
                        count = int(count_str)
                        logger.info(f"eBay: Encontrados {count} items para '{keyword}'")
                        time.sleep(self.delay)
                        return count

                    # Si no encuentra nada, asumimos 0 pero avisamos
                    logger.warning(f"eBay: No se encontró el número para '{keyword}'")

                elif response.status_code == 429:
                    logger.warning(f"eBay rate limit hit. Waiting 10s...")
                    time.sleep(10)

            except Exception as e:
                logger.error(f"Error scraping eBay: {e}")

        return 0

    def scrape_amazon(self, keyword: str) -> Optional[int]:
        """
        Scrape Amazon search results count (Versión compatible con MX y US).
        """
        # ⚠️ CAMBIO IMPORTANTE:
        # Si quieres resultados de México (como tu foto), usa .com.mx
        # Si tus keywords son en inglés (plush, toy), quizás prefieras .com
        domain = "amazon.com.mx"
        url = f"https://www.{domain}/s?k={keyword.replace(' ', '+')}"

        for attempt in range(self.max_retries):
            try:
                # Headers rotativos para engañar a Amazon
                headers = {
                    "User-Agent": self.ua.random,
                    "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",  # Prioridad español
                    "Referer": "https://www.google.com/",
                }

                response = self.session.get(url, headers=headers, timeout=10)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "html.parser")
                    page_text = soup.get_text()

                    # --- ZONA DE DETECCIÓN (REGEX) ---
                    # Tu foto dice: "1 a 48 de 643 resultados"
                    # Este regex busca: "de" + espacio + "643" + espacio + "resultados"
                    match = re.search(
                        r"(?:of|de)\s+(?:over|más de)?\s*([\d,.]+)\s+(?:results|resultados)",
                        page_text,
                        re.IGNORECASE,
                    )

                    if match:
                        # Limpiamos puntos o comas del número (ej. 1.000 -> 1000)
                        count_str = match.group(1).replace(",", "").replace(".", "")
                        logger.info(
                            f"Amazon ({domain}): Encontrados {count_str} items para '{keyword}'"
                        )
                        time.sleep(self.delay)
                        return int(count_str)

                    # Intento secundario (por si cambia el diseño)
                    match_simple = re.search(
                        r"([\d,.]+)\s+(?:results|resultados)", page_text, re.IGNORECASE
                    )
                    if match_simple:
                        count_str = (
                            match_simple.group(1).replace(",", "").replace(".", "")
                        )
                        return int(count_str)

                    logger.warning(
                        f"Amazon: No se encontró el número para '{keyword}' (Posible Captcha)"
                    )

                elif response.status_code == 503:
                    logger.warning("Amazon 503 (Servidor ocupado o Detectado)")
                    time.sleep(20)

            except Exception as e:
                logger.error(f"Error scraping Amazon: {e}")

        return 0

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
                results["ebay_count"] = count if count is not None else -1

            elif platform.lower() == "amazon":
                count = self.scrape_amazon(keyword)
                results["amazon_count"] = count if count is not None else -1

        # Calculate total supply
        counts = [v for k, v in results.items() if k.endswith("_count") and v >= 0]
        results["total_supply"] = sum(counts) if counts else -1

        return results


def demo():
    """Demo function to test the scraper."""
    scraper = MarketplaceScraper(delay=2)

    test_keywords = ["clash royale plush", "skibidi toilet toy", "digital circus plush"]

    print("\n=== Testing eBay Scraper ===")
    for keyword in test_keywords:
        result = scraper.get_supply_metrics(keyword, platforms=["ebay"])
        print(f"{keyword}: {result}")


if __name__ == "__main__":
    demo()
