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
        """
        Calcula el score y añade etiquetas de mercado y recomendaciones.
        """
        # --- PASO CRÍTICO: Calcular el score primero ---
        # Usamos interest_score como demanda y total_supply como oferta
        df["opportunity_score"] = df.apply(
            lambda x: self.calculate_opportunity_score(x["interest_score"], x["total_supply"]), 
            axis=1
        )

        def classify_market(row):
            supply = row["total_supply"]
            if supply < 100: return "Low Supply (Blue Ocean) 🌊"
            if supply < 500: return "Moderate Supply 🟢"
            return "Saturated Market 🔴"

        df["market_status"] = df.apply(classify_market, axis=1)

        def get_recommendation(row):
            # Verificamos que la columna exista por seguridad
            score = row.get("opportunity_score", 0)
            
            if row.get("is_rising") is False:
                return "Avoid ❌ (Stagnant)"

            if score > 1.0:
                return "STRONG BUY 🚀"
            elif score > 0.5:
                return "Consider 💡"
            elif score > 0.1:
                return "Risky ⚠️"
            else:
                return "Avoid ❌ (Saturated)"

        df["recommendation"] = df.apply(get_recommendation, axis=1)
        return df

    def generate_report(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        opportunities = self.add_classifications(df)

        # Agregamos 'history' a la lista de columnas permitidas
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
            "history", # <--- CRÍTICO: Para que la gráfica reciba datos
            "amazon_count",
            "ebay_count"
        ]

        # Solo filtramos las que realmente existan en el DataFrame
        report_columns = [c for c in report_columns if c in opportunities.columns]
        
        # IMPORTANTE: Quitamos el .head(top_n) si quieres ver todos los resultados en el dashboard
        report = opportunities[report_columns].head(top_n)

        if not report.empty:
            report.insert(0, "rank", range(1, len(report) + 1))

        logger.info(f"Generated report with {len(report)} opportunities")
        return report

    def save_report(self, df: pd.DataFrame, filepath: str):
        df.to_csv(filepath, index=False)
        logger.info(f"Report saved to {filepath}")
        print(f"\n✅ Report saved: {filepath}")
