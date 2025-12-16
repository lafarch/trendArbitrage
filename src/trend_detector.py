"""
Phase 1: Trend Detection Module
================================
Purpose: Identify high-demand keywords using Google Trends API

Why pytrends?
- Free access to Google Trends data
- No API key required
- Returns normalized interest scores (0-100)
- Can detect rising searches and related queries

Algorithm:
1. Fetch daily trending searches OR analyze specific keywords
2. Extract interest over time (velocity check)
3. Filter for keywords with rising momentum
"""

import pandas as pd
from pytrends.request import TrendReq
import time
from typing import List, Dict, Optional
import logging
import random

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrendDetector:
    """
    Detects trending keywords and measures their search interest velocity.
    """
    
    def __init__(self, geo: str = "US", timeframe: str = "now 7-d"):
        """
        Initialize the Google Trends API client.
        
        Args:
            geo: Country code (US, GB, etc.)
            timeframe: Time window for trend analysis
                      Options: 'now 1-H', 'now 4-H', 'now 1-d', 'now 7-d', 'today 1-m'
        """
        self.geo = geo
        self.timeframe = timeframe
        
        # Initialize pytrends with custom settings to avoid rate limits
        self.pytrends = TrendReq(
            hl='en-US',
            tz=360,
            timeout=(10, 25),  # Connect timeout, read timeout
            retries=2,
            backoff_factor=0.5
        )

        time.sleep(random.uniform(3, 8))

        logger.info(f"TrendDetector initialized for {geo} with timeframe {timeframe}")
    
    def get_daily_trending_searches(self) -> List[str]:
        """
        Fetch today's trending searches from Google Trends.
        
        Returns:
            List of trending keyword strings
            
        Why this matters:
        - These are REAL-TIME trends that people are searching NOW
        - First-mover advantage: catch trends before markets saturate
        """
        try:
            # Get trending searches for the specified country
            trending_df = self.pytrends.trending_searches(pn=self.geo.lower())
            
            # Convert DataFrame to list
            trending_keywords = trending_df[0].tolist()
            
            logger.info(f"Fetched {len(trending_keywords)} trending searches")
            return trending_keywords[:20]  # Return top 20
            
        except Exception as e:
            logger.error(f"Error fetching trending searches: {e}")
            return []
    
    def get_interest_over_time(self, keywords: List[str]) -> pd.DataFrame:
        results = []
        
        # Process only 2 keywords at a time (instead of 5)
        for i in range(0, len(keywords), 2):
            batch = keywords[i : i + 2]
            
            try:
                # Build payload for this batch
                self.pytrends.build_payload(
                    batch,
                    cat=0,
                    timeframe=self.timeframe,
                    geo=self.geo,
                )
                
                # Get interest over time
                interest_df = self.pytrends.interest_over_time()
                
                if not interest_df.empty:
                    interest_df = interest_df.drop(
                        columns=["isPartial"], errors="ignore"
                    )
                    
                    # Calculate metrics for each keyword
                    for keyword in batch:
                        if keyword in interest_df.columns:
                            scores = interest_df[keyword].values
                            
                            current_interest = scores[-1]
                            
                            early_avg = scores[:2].mean() if len(scores) >= 2 else 0
                            recent_avg = (
                                scores[-2:].mean()
                                if len(scores) >= 2
                                else current_interest
                            )
                            is_rising = recent_avg > early_avg * 1.5
                            
                            results.append(
                                {
                                    "keyword": keyword,
                                    "interest_score": int(current_interest),
                                    "is_rising": is_rising,
                                    "velocity": round(recent_avg - early_avg, 2),
                                }
                            )
                            
                            logger.info(f"✓ {keyword}: interest={int(current_interest)}")
                
                # CRITICAL: Long random delay between requests
                delay = random.uniform(20, 30)
                logger.info(f"⏳ Waiting {delay:.1f}s before next batch...")
                time.sleep(delay)
                
            except Exception as e:
                logger.error(f"Error analyzing keywords {batch}: {e}")
                # If we hit an error, wait even LONGER
                logger.warning("⚠️  Error encountered, waiting 60s before continuing...")
                time.sleep(60)
                continue
        
        df = pd.DataFrame(results)
        logger.info(f"Analyzed {len(df)} keywords for interest scores")
        return df
    
    def filter_high_velocity_trends(
        self, 
        trend_df: pd.DataFrame, 
        min_interest: int = 20
    ) -> pd.DataFrame:
        """
        Filter trends to keep only high-momentum keywords.
        
        Args:
            trend_df: DataFrame from get_interest_over_time()
            min_interest: Minimum interest score to consider
            
        Returns:
            Filtered DataFrame with only promising trends
            
        Why filter?
        - We want RISING trends (early signals)
        - We want SUFFICIENT volume (enough demand to profit)
        """
        filtered = trend_df[
            (trend_df['interest_score'] >= min_interest) &
            (trend_df['is_rising'] == True)
        ].copy()
        
        # Sort by velocity (fastest growing first)
        filtered = filtered.sort_values('velocity', ascending=False)
        
        logger.info(f"Filtered to {len(filtered)} high-velocity trends")
        return filtered


def demo():
    """Demo function to test the trend detector."""
    detector = TrendDetector(geo="US", timeframe="now 7-d")
    
    # Option 1: Get today's trending searches
    print("\n=== Today's Trending Searches ===")
    trending = detector.get_daily_trending_searches()
    print(trending[:10])
    
    # Option 2: Analyze specific keywords
    print("\n=== Analyzing Specific Keywords ===")
    test_keywords = [
        "clash royale plush",
        "skibidi toilet toy",
        "digital circus plush",
        "poppy playtime toy",
        "among us plush"
    ]
    
    interest_df = detector.get_interest_over_time(test_keywords)
    print(interest_df)
    
    # Filter for high-velocity trends
    print("\n=== High-Velocity Opportunities ===")
    opportunities = detector.filter_high_velocity_trends(interest_df, min_interest=10)
    print(opportunities)


if __name__ == "__main__":
    demo()
