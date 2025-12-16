import pandas as pd
import logging

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

    def calculate_opportunity_score(self, interest_score: float, supply_count: int) -> float:
        if supply_count < 0 or interest_score <= 0:
            return 0.0
        return round(interest_score / (supply_count + 1), 4)

    def merge_and_score(self, trend_df: pd.DataFrame, supply_df: pd.DataFrame) -> pd.DataFrame:
        merged = pd.merge(trend_df, supply_df, on="keyword", how="inner")

        merged["opportunity_score"] = merged.apply(
            lambda row: self.calculate_opportunity_score(
                row["interest_score"], row["total_supply"]
            ),
            axis=1,
        )

        return merged

    def add_classifications(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        def classify_market(supply):
            if supply < 50:
                return "Underserved ⭐⭐⭐"
            elif supply < 200:
                return "Low Competition ⭐⭐"
            elif supply < 500:
                return "Moderate Competition ⭐"
            else:
                return "Oversaturated ❌"

        df["market_status"] = df["total_supply"].apply(classify_market)

        def recommendation(row):
            amazon_supply = row.get("amazon_count", 0)

            # 🔴 HARD OVERRIDE RULE
            if amazon_supply >= 3000:
                return "AVOID ❌ (Amazon-dominated)"

            if not row.get("is_rising", False):
                return "Avoid ❌ (Stagnant)"

            score = row["opportunity_score"]
            if score > 1.0:
                return "STRONG BUY 🚀"
            elif score > 0.5:
                return "Consider 💡"
            elif score > 0.1:
                return "Risky ⚠️"
            else:
                return "Avoid ❌ (Saturated)"

        df["recommendation"] = df.apply(recommendation, axis=1)
        return df

    def generate_report(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        df = self.add_classifications(df)

        cols = [
            "keyword",
            "interest_score",
            "amazon_count",
            "ebay_count",
            "walmart_count",
            "aliexpress_count",
            "total_supply",
            "opportunity_score",
            "market_status",
            "recommendation",
            "is_rising",
            "velocity",
        ]
        cols = [c for c in cols if c in df.columns]

        report = df[cols].head(top_n).copy()
        report.insert(0, "rank", range(1, len(report) + 1))
        return report

    def save_report(self, df: pd.DataFrame, filepath: str):
        df.to_csv(filepath, index=False)
        logger.info(f"Report saved to {filepath}")
        print(f"\n✅ Report saved: {filepath}")
