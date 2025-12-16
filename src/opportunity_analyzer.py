"""
Phase 4: Opportunity Analyzer Module
=====================================
Purpose: Calculate the "Opportunity Score" and identify winning products

The Digital Arbitrage Formula:
------------------------------
Opportunity Score = Interest Score / (Supply Count + 1)

Why this works:
- HIGH Interest + LOW Supply = High Score (OPPORTUNITY!)
- LOW Interest + HIGH Supply = Low Score (Avoid)
- The "+1" prevents division by zero

Example:
- Product A: Interest=80, Supply=50  → Score = 1.60 ⭐⭐⭐
- Product B: Interest=80, Supply=5000 → Score = 0.016 ❌
- Product C: Interest=20, Supply=10   → Score = 1.82 ⭐⭐⭐⭐

We want Product A and C!
"""

import pandas as pd
import numpy as np
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpportunityAnalyzer:
    """
    Combines demand and supply data to identify profitable niches.
    """

    def __init__(self, min_interest: int = 20, max_supply: int = 500):
        """
        Initialize analyzer with filtering thresholds.

        Args:
            min_interest: Minimum Google Trends score to consider
            max_supply: Maximum product count to consider (above = saturated)
        """
        self.min_interest = min_interest
        self.max_supply = max_supply
        logger.info(
            f"OpportunityAnalyzer initialized (min_interest={min_interest}, max_supply={max_supply})"
        )

    def calculate_opportunity_score(
        self, interest_score: float, supply_count: int
    ) -> float:
        """
        Calculate the opportunity score for a single product.

        Args:
            interest_score: Google Trends interest (0-100)
            supply_count: Number of existing products on marketplace

        Returns:
            Opportunity score (higher = better opportunity)

        The Math:
        ---------
        Score = Demand / Supply

        This creates a "demand density" metric:
        - If 100 people search but only 10 products exist → High density
        - If 100 people search but 10,000 products exist → Low density
        """
        # Handle edge cases
        if supply_count < 0:  # Scraping failed
            return 0.0

        if interest_score <= 0:
            return 0.0

        # The formula
        score = interest_score / (supply_count + 1)

        return round(score, 4)

    def merge_and_score(
        self, trend_df: pd.DataFrame, supply_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Merge trend data with supply data and calculate scores.

        Args:
            trend_df: DataFrame with columns [keyword, interest_score, is_rising]
            supply_df: DataFrame with columns [keyword, total_supply]

        Returns:
            Combined DataFrame with opportunity_score column
        """
        # Merge on keyword
        merged = pd.merge(trend_df, supply_df, on="keyword", how="inner")

        # Calculate opportunity score for each row
        merged["opportunity_score"] = merged.apply(
            lambda row: self.calculate_opportunity_score(
                row["interest_score"], row["total_supply"]
            ),
            axis=1,
        )

        logger.info(f"Calculated opportunity scores for {len(merged)} products")
        return merged

    def filter_opportunities(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter to keep only real opportunities.

        Args:
            df: DataFrame with opportunity scores

        Returns:
            Filtered DataFrame with only promising products

        Filters Applied:
        1. Minimum interest (enough demand)
        2. Maximum supply (not oversaturated)
        3. Must be rising trend
        4. Supply data must be valid (not -1)
        """
        filtered = df[
            (df["interest_score"] >= self.min_interest)
            & (df["total_supply"] <= self.max_supply)
            & (df["total_supply"] >= 0)  # Valid data
            & (df["is_rising"] == True)
        ].copy()

        # Sort by opportunity score (best first)
        filtered = filtered.sort_values("opportunity_score", ascending=False)

        logger.info(f"Filtered to {len(filtered)} high-opportunity products")
        return filtered

    def add_classifications(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add human-readable classifications to help interpret results.
        """
        # IMPORTANTE: Trabajamos sobre una copia para no romper el original
        df = df.copy()

        # Classify market saturation
        def classify_market(supply):
            if supply < 0:
                return "Unknown"
            elif supply < 50:
                return "Underserved ⭐⭐⭐"
            elif supply < 200:
                return "Low Competition ⭐⭐"
            elif supply < 500:
                return "Moderate Competition ⭐"
            else:
                return "Oversaturated ❌"

        df["market_status"] = df["total_supply"].apply(classify_market)

        # Add recommendation (LÓGICA NUEVA QUE AGREGAMOS)
        def get_recommendation(row):
            # REGLA 1: Si no está creciendo, castigarlo inmediatamente.
            if row.get("is_rising") == False:
                return "Avoid ❌ (Stagnant)"

            # REGLA 2: Si está creciendo, entonces miramos el Score
            if row["opportunity_score"] > 1.0:
                return "STRONG BUY 🚀"
            elif row["opportunity_score"] > 0.5:
                return "Consider 💡"
            elif row["opportunity_score"] > 0.1:
                return "Risky ⚠️"
            else:
                return "Avoid ❌ (Saturated)"

        df["recommendation"] = df.apply(get_recommendation, axis=1)

        return df  # <--- ¡ESTA ES LA LÍNEA QUE FALTABA!

    def generate_report(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """
        Generate final report with ALL analyzed products.
        """
        # NO FILTRAMOS, pasamos todos los datos
        # opportunities = self.filter_opportunities(df)

        opportunities = df.copy()  # Usamos todo lo que llegó

        # Add classifications
        opportunities = self.add_classifications(opportunities)

        # Select and reorder columns for readability
        report_columns = [
            "keyword",
            "interest_score",
            "total_supply",
            "opportunity_score",
            "market_status",
            "recommendation",
            "is_rising",
            "velocity",
        ]

        # Keep only columns that exist
        report_columns = [col for col in report_columns if col in opportunities.columns]
        report = opportunities[report_columns].head(top_n)

        # Add ranking
        report.insert(0, "rank", range(1, len(report) + 1))

        logger.info(f"Generated report with {len(report)} opportunities")
        return report

    def save_report(self, df: pd.DataFrame, filepath: str):
        """
        Save the opportunity report to CSV.

        Args:
            df: Report DataFrame
            filepath: Output file path
        """
        df.to_csv(filepath, index=False)
        logger.info(f"Report saved to {filepath}")
        print(f"\n✅ Report saved: {filepath}")


def demo():
    """Demo function to test the analyzer."""
    # Mock data for demonstration
    trend_data = pd.DataFrame(
        {
            "keyword": ["clash royale plush", "skibidi toilet toy", "generic toy"],
            "interest_score": [75, 85, 30],
            "is_rising": [True, True, False],
            "velocity": [15.5, 20.2, 2.1],
        }
    )

    supply_data = pd.DataFrame(
        {
            "keyword": ["clash royale plush", "skibidi toilet toy", "generic toy"],
            "total_supply": [45, 120, 5000],
        }
    )

    # Initialize analyzer
    analyzer = OpportunityAnalyzer(min_interest=20, max_supply=500)

    # Merge and score
    print("\n=== Merged Data ===")
    scored_df = analyzer.merge_and_score(trend_data, supply_data)
    print(scored_df)

    # Generate report
    print("\n=== Opportunity Report ===")
    report = analyzer.generate_report(scored_df, top_n=5)
    print(report)

    # Show interpretation
    print("\n=== Interpretation ===")
    print("🚀 STRONG BUY: High demand, low supply - act fast!")
    print("💡 Consider: Good opportunity, some competition")
    print("⚠️  Risky: Moderate competition or unclear data")
    print("❌ Avoid: Oversaturated or low demand")


if __name__ == "__main__":
    demo()
