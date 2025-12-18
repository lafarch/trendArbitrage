"""
Phase 1: Trend Detection Module (SerpApi Version)
==================================================
Purpose: Identify high-demand keywords using SerpApi's Google Trends wrapper

Why SerpApi?
- No rate limits (within your plan)
- No IP bans or CAPTCHAs
- Handles all anti-bot measures automatically
- Returns clean, structured JSON data
- Costs: $50/month for 5,000 searches (or 100 free/month)

Algorithm:
1. Fetch trending searches OR analyze specific keywords
2. Extract interest over time data
3. Filter for keywords with rising momentum
"""

import pandas as pd
import time
from typing import List, Dict, Optional
import logging
from serpapi.google_search import GoogleSearch
import os
from dotenv import load_dotenv
import numpy as np

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def compute_trend_slope(values: list) -> float:
    if len(values) < 2:
        return 0.0
    x = np.arange(len(values))
    slope = np.polyfit(x, values, 1)[0]
    return round(float(slope), 3)


def compute_consistency(values: list) -> float:
    mean = np.mean(values)
    if mean == 0:
        return 0.0
    return round(1 - (np.std(values) / mean), 3)


def detect_recent_spike(values: list) -> bool:
    if len(values) < 6:
        return False
    recent = values[-1]
    baseline = np.mean(values[:-3])
    return recent > baseline * 1.3


class TrendDetector:
    """
    Detects trending keywords using SerpApi's Google Trends API.
    """

    def __init__(self, geo: str = "US", timeframe: str = "today 12-m"):
        self.geo = geo
        self.timeframe = timeframe
        self.api_key = os.getenv("SERPAPI_KEY")

        if not self.api_key:
            raise ValueError("❌ SERPAPI_KEY not found!")
        
        logger.info(f"TrendDetector initialized: {geo} | {timeframe}")

    def get_daily_trending_searches(self, limit: int = 20) -> List[str]:
        """
        Fetch today's trending searches using SerpApi.

        Args:
            limit: Maximum number of trending keywords to return

        Returns:
            List of trending keyword strings
        """
        try:
            params = {
                "engine": "google_trends_trending_now",
                "frequency": "daily",
                "geo": self.geo,
                "api_key": self.api_key,
            }

            search = GoogleSearch(params)
            results = search.get_dict()

            # Extract trending searches
            trending_searches = results.get("trending_searches", [])
            keywords = [item.get("query") for item in trending_searches[:limit]]

            logger.info(f"Fetched {len(keywords)} trending searches")
            return keywords

        except Exception as e:
            logger.error(f"Error fetching trending searches: {e}")
            return []

    def get_interest_over_time(self, keywords: List[str]) -> pd.DataFrame:
        results = []

        for keyword in keywords:
            try:
                logger.info(f"📊 Analyzing: {keyword}")
                
                params = {
                    "engine": "google_trends",
                    "q": keyword,
                    "data_type": "TIMESERIES",
                    "date": self.timeframe, # Usará "today 12-m"
                    "geo": self.geo,
                    "api_key": self.api_key,
                }

                search = GoogleSearch(params)
                data = search.get_dict()
                timeline_data = data.get("interest_over_time", {}).get("timeline_data", [])

                if timeline_data:
                    values = []
                    history_points = [] # Lista para guardar fecha y valor
                    
                    for item in timeline_data:
                        # Extraer el valor numérico
                        val = item.get("values", [{}])[0].get("value", 0)
                        # Extraer la fecha (string que luego procesará JS)
                        date_val = item.get("date", "") 
                        
                        try:
                            v_int = int(val) if val else 0
                            values.append(v_int)
                            # Guardamos el par fecha/valor
                            if date_val:
                                history_points.append({"date": date_val, "value": v_int})
                        except:
                            values.append(0)

                    # Métricas calculadas
                    avg_interest = round(float(np.mean(values)), 2)
                    trend_slope = compute_trend_slope(values)
                    trend_consistency = compute_consistency(values)
                    recent_spike = detect_recent_spike(values)
                    is_rising = trend_slope > 0
                    
                    # Score simple (manteniendo tu lógica)
                    viability_score = 0
                    if avg_interest >= 20: viability_score += 25
                    if trend_slope > 0: viability_score += 25
                    if trend_consistency >= 0.5: viability_score += 20
                    if recent_spike: viability_score += 15
                    if avg_interest >= 50: viability_score += 15

                    results.append({
                        "keyword": keyword,
                        "interest_score": avg_interest,
                        "trend_slope": trend_slope,
                        "trend_consistency": trend_consistency,
                        "recent_spike": recent_spike,
                        "viability_score": viability_score,
                        "is_rising": is_rising,
                        "velocity": trend_slope,
                        # CAMBIO 3: Devolvemos la historia cruda
                        "history": history_points 
                    })
                else:
                    logger.warning(f"⚠️ No data for '{keyword}'")
                
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"Error analyzing keyword '{keyword}': {e}")
                continue

        df = pd.DataFrame(results)
        
        # Manejo de dataframe vacío
        if df.empty:
            return pd.DataFrame(columns=["keyword", "interest_score", "viability_score", "history"])

        return df

    def filter_high_velocity_trends(
        self, trend_df: pd.DataFrame, min_interest: int = 20
    ) -> pd.DataFrame:
        """
        Filter trends to keep only products with sufficient interest.

        Args:
            trend_df: DataFrame from get_interest_over_time()
            min_interest: Minimum interest score to consider

        Returns:
            Filtered DataFrame
        """
        filtered = trend_df[(trend_df["interest_score"] >= min_interest)].copy()

        # Sort by velocity (fastest growing first)
        filtered = filtered.sort_values("velocity", ascending=False)

        logger.info(f"Filtered to {len(filtered)} products (including non-rising)")
        return filtered


def demo():
    """Demo function to test the SerpApi trend detector."""
    detector = TrendDetector(geo="US", timeframe="today 3-m")

    # Option 1: Get today's trending searches
    print("\n=== Today's Trending Searches ===")
    trending = detector.get_daily_trending_searches(limit=10)
    for i, keyword in enumerate(trending, 1):
        print(f"{i}. {keyword}")

    # Option 2: Analyze specific keywords
    print("\n=== Analyzing Specific Keywords ===")
    test_keywords = [
        "clash royale plush",
        "skibidi toilet toy",
        "digital circus plush",
    ]

    interest_df = detector.get_interest_over_time(test_keywords)
    print("\n", interest_df)

    # Filter for opportunities
    print("\n=== High-Interest Keywords ===")
    opportunities = detector.filter_high_velocity_trends(interest_df, min_interest=10)
    print(opportunities)


if __name__ == "__main__":
    demo()
