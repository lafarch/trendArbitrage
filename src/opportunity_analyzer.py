"""
Phase 4: Opportunity Analyzer Module (Demand-Aware Version)
===========================================================
Purpose: Calculate the "Opportunity Score" and identify winning products

Key change:
- Uses viability_score (absolute demand signal) when present
- Falls back to interest_score for backward compatibility
"""

import pandas as pd
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpportunityAnalyzer:
    """
    Combines demand and supply data to identify profitable niches.
    """

    def __init__(self, min_interest: int = 20, max_supply: int = 500):
        self.min_interest = min_interest
        self.max_supply = max_supply
        logger.info(
            f"OpportunityAnalyzer initialized (min_interest={min_interest}, max_supply={max_supply})"
        )

    # ------------------------------------------------------------------
    # Demand / Supply math
    # ------------------------------------------------------------------

    def calculate_opportunity_score(self, demand: float, supply: int) -> float:
        """
        Opportunity Score = Demand / (Supply + 1)

        Demand:
        - viability_score if available (0-100)
        - otherwise interest_score (0-100)
        """
        if supply < 0 or demand <= 0:
            return 0.0

        score = demand / (supply + 1)
        return round(score, 4)

    # ------------------------------------------------------------------
    # Core pipeline step
    # ------------------------------------------------------------------

    def merge_and_score(
        self, trend_df: pd.DataFrame, supply_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Merge demand and supply data and calculate opportunity scores.
        """
        merged = pd.merge(trend_df, supply_df, on="keyword", how="inner")

        # Decide which demand signal to use
        if "viability_score" in merged.columns:
            logger.info("Using viability_score as demand signal")
            merged["demand_signal"] = merged["viability_score"]
        else:
            logger.warning("viability_score not found, falling back to interest_score")
            merged["demand_signal"] = merged["interest_score"]

        merged["opportunity_score"] = merged.apply(
            lambda row: self.calculate_opportunity_score(
                row["demand_signal"], row["total_supply"]
            ),
            axis=1,
        )

        logger.info(f"Calculated opportunity scores for {len(merged)} products")
        return merged

    # ------------------------------------------------------------------
    # Classification & reporting
    # ------------------------------------------------------------------

    def add_classifications(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

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

        def get_recommendation(row):
            if row.get("is_rising") is False:
                return "Avoid ❌ (Stagnant)"

            if row["opportunity_score"] > 1.0:
                return "STRONG BUY 🚀"
            elif row["opportunity_score"] > 0.5:
                return "Consider 💡"
            elif row["opportunity_score"] > 0.1:
                return "Risky ⚠️"
            else:
                return "Avoid ❌ (Saturated)"

        df["recommendation"] = df.apply(get_recommendation, axis=1)
        return df

    def generate_report(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        opportunities = self.add_classifications(df)

        report_columns = [
            "keyword",
            "demand_signal",
            "interest_score",
            "viability_score",
            "total_supply",
            "opportunity_score",
            "market_status",
            "recommendation",
            "is_rising",
            "velocity",
        ]

        report_columns = [c for c in report_columns if c in opportunities.columns]
        report = opportunities[report_columns].head(top_n)

        report.insert(0, "rank", range(1, len(report) + 1))

        logger.info(f"Generated report with {len(report)} opportunities")
        return report

    def save_report(self, df: pd.DataFrame, filepath: str):
        df.to_csv(filepath, index=False)
        logger.info(f"Report saved to {filepath}")
        print(f"\n✅ Report saved: {filepath}")
