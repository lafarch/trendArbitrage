"""
Phase 1: Trend Detection Module (Enhanced with Commercial Metrics)
==================================================================
Purpose: Identify high-demand keywords with real search volumes and purchase intent

Data Sources:
- SerpApi Google Trends: Historical interest patterns
- SerpApi Google Shopping: Purchase intent signals (price, product count)
- Internal estimation: Conversion rates based on market signals

Key Outputs:
- Real monthly search volumes (scaled from relative interest)
- Purchase intent scores (0-100)
- Multi-timeframe analysis (7d, 1m, 3m, 6m, 12m)
"""

import pandas as pd
import time
from typing import List, Dict, Optional
import logging
from serpapi.google_search import GoogleSearch
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def compute_trend_slope(values: list) -> float:
    """Calcula la pendiente de crecimiento."""
    if len(values) < 2:
        return 0.0
    x = np.arange(len(values))
    slope = np.polyfit(x, values, 1)[0]
    return round(float(slope), 3)


def compute_consistency(values: list) -> float:
    """Mide qué tan estable es el interés (1 = muy consistente, 0 = volátil)."""
    mean = np.mean(values)
    if mean == 0:
        return 0.0
    return round(1 - (np.std(values) / mean), 3)


def detect_recent_spike(values: list) -> bool:
    """Detecta si hubo un pico reciente vs el baseline."""
    if len(values) < 6:
        return False
    recent = values[-1]
    baseline = np.mean(values[:-3])
    return recent > baseline * 1.3


class TrendDetector:
    """
    Detects trending keywords using SerpApi's Google Trends API.
    Enhanced with purchase intent estimation and temporal analysis.
    """

    def __init__(self, geo: str = "US", timeframe: str = "today 12-m"):
        self.geo = geo
        self.timeframe = timeframe
        self.api_key = os.getenv("SERPAPI_KEY")

        if not self.api_key:
            raise ValueError("❌ SERPAPI_KEY not found!")
        
        logger.info(f"TrendDetector initialized: {geo} | {timeframe}")

    # ==========================================
    # TRENDING SEARCHES
    # ==========================================

    def get_daily_trending_searches(self, limit: int = 20) -> List[str]:
        """Fetch today's trending searches using SerpApi."""
        try:
            params = {
                "engine": "google_trends_trending_now",
                "frequency": "daily",
                "geo": self.geo,
                "api_key": self.api_key,
            }

            search = GoogleSearch(params)
            results = search.get_dict()

            trending_searches = results.get("trending_searches", [])
            keywords = [item.get("query") for item in trending_searches[:limit]]

            logger.info(f"Fetched {len(keywords)} trending searches")
            return keywords

        except Exception as e:
            logger.error(f"Error fetching trending searches: {e}")
            return []

    # ==========================================
    # PURCHASE INTENT ESTIMATION
    # ==========================================

    def get_purchase_intent(self, keyword: str) -> Dict:
        """
        Estima intención de compra usando Google Shopping (SerpApi).
        
        Factores:
        1. Shopping results disponibles (40 pts)
        2. Precio promedio existe = mercado activo (30 pts)
        3. Variedad de productos (30 pts)
        
        Returns:
            {
                'shopping_results': 150,
                'avg_price': 24.99,
                'purchase_intent_score': 75  # 0-100
            }
        """
        try:
            params = {
                "engine": "google_shopping",
                "q": keyword,
                "api_key": self.api_key,
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            shopping_results = results.get("shopping_results", [])
            total_results = results.get("search_information", {}).get("total_results", 0)
            
            # Extraer precios de los primeros 20 resultados
            prices = []
            for item in shopping_results[:20]:
                price_str = item.get("extracted_price", 0)
                if price_str:
                    try:
                        prices.append(float(price_str))
                    except:
                        continue
            
            avg_price = round(np.mean(prices), 2) if prices else 0
            
            # CALCULAR PURCHASE INTENT (0-100)
            purchase_intent = 0
            
            # Factor 1: Disponibilidad de productos en Shopping (0-40 pts)
            if total_results > 0:
                purchase_intent += min(40, (total_results / 100) * 10)
            
            # Factor 2: Precio promedio existe = mercado activo (0-30 pts)
            if avg_price > 0:
                purchase_intent += 30
            
            # Factor 3: Variedad de precios = mercado competitivo (0-30 pts)
            if len(prices) >= 10:
                purchase_intent += 30
            elif len(prices) >= 5:
                purchase_intent += 15
            
            logger.info(f"Purchase intent for '{keyword}': {purchase_intent:.1f}/100")
            
            return {
                "shopping_results": total_results,
                "avg_price": avg_price,
                "purchase_intent_score": round(purchase_intent, 1),
            }
            
        except Exception as e:
            logger.warning(f"Could not fetch shopping data for '{keyword}': {e}")
            return {
                "shopping_results": 0,
                "avg_price": 0,
                "purchase_intent_score": 0,
            }

    def estimate_conversion_rate(self, purchase_intent: float) -> float:
        """
        Estima conversion rate basado en purchase intent.
        
        Benchmarks dropshipping:
        - High intent (70-100): 2.5-3.5%
        - Medium intent (40-70): 1.5-2.5%
        - Low intent (0-40): 0.5-1.5%
        
        Returns: Decimal (0.025 = 2.5%)
        """
        if purchase_intent >= 70:
            return 0.03  # 3%
        elif purchase_intent >= 50:
            return 0.025  # 2.5%
        elif purchase_intent >= 30:
            return 0.015  # 1.5%
        else:
            return 0.01  # 1%

    def scale_to_real_searches(self, relative_interest: float, baseline: int = 10000) -> int:
        """
        Convierte interés relativo (0-100) a búsquedas mensuales estimadas.
        
        Lógica:
        - 100 de interés = baseline búsquedas/mes (default 10,000)
        - 50 de interés = baseline/2 (5,000)
        - 10 de interés = baseline/10 (1,000)
        
        Esto da números reales que podemos monetizar.
        """
        if relative_interest <= 0:
            return 0
        
        # Escala lineal con el baseline
        estimated = int((relative_interest / 100) * baseline)
        return max(estimated, 100)  # Mínimo 100 búsquedas/mes

    # ==========================================
    # INTEREST OVER TIME (Enhanced)
    # ==========================================

    def get_interest_over_time(self, keywords: List[str]) -> pd.DataFrame:
        """
        Analiza interés histórico + datos comerciales para cada keyword.
        
        Returns DataFrame con:
        - keyword, interest_score, viability_score
        - monthly_searches (real), purchase_intent_score, avg_price
        - estimated_conversion_rate, estimated_monthly_buyers
        - trend_slope, is_rising, history
        """
        results = []

        for keyword in keywords:
            try:
                logger.info(f"📊 Analyzing: {keyword}")
                
                # 1. Obtener datos de Google Trends
                params = {
                    "engine": "google_trends",
                    "q": keyword,
                    "data_type": "TIMESERIES",
                    "date": self.timeframe,
                    "geo": self.geo,
                    "api_key": self.api_key,
                }

                search = GoogleSearch(params)
                data = search.get_dict()
                timeline_data = data.get("interest_over_time", {}).get("timeline_data", [])

                if not timeline_data:
                    logger.warning(f"⚠️ No trend data for '{keyword}'")
                    continue

                # Extraer valores e historia
                values = []
                history_points = []
                
                for item in timeline_data:
                    val = item.get("values", [{}])[0].get("value", 0)
                    date_val = item.get("date", "")
                    
                    try:
                        v_int = int(val) if val else 0
                        values.append(v_int)
                        if date_val:
                            history_points.append({"date": date_val, "value": v_int})
                    except:
                        values.append(0)

                # Métricas de demanda
                avg_interest = round(float(np.mean(values)), 2)
                trend_slope = compute_trend_slope(values)
                trend_consistency = compute_consistency(values)
                recent_spike = detect_recent_spike(values)
                is_rising = trend_slope > 0
                
                # Viability score (0-100)
                viability_score = 0
                if avg_interest >= 20: viability_score += 25
                if trend_slope > 0: viability_score += 25
                if trend_consistency >= 0.5: viability_score += 20
                if recent_spike: viability_score += 15
                if avg_interest >= 50: viability_score += 15

                # 2. Obtener datos comerciales (purchase intent)
                purchase_data = self.get_purchase_intent(keyword)
                
                # 3. Escalar a búsquedas mensuales reales
                monthly_searches = self.scale_to_real_searches(avg_interest)
                
                # 4. Estimar conversion rate
                conversion_rate = self.estimate_conversion_rate(
                    purchase_data["purchase_intent_score"]
                )
                
                # 5. Calcular compradores mensuales estimados
                monthly_buyers = int(monthly_searches * conversion_rate)

                # Compilar resultado
                results.append({
                    "keyword": keyword,
                    "interest_score": avg_interest,
                    "trend_slope": trend_slope,
                    "trend_consistency": trend_consistency,
                    "recent_spike": recent_spike,
                    "viability_score": viability_score,
                    "is_rising": is_rising,
                    "velocity": trend_slope,
                    "history": history_points,
                    # Nuevos campos comerciales
                    "monthly_searches": monthly_searches,
                    "purchase_intent_score": purchase_data["purchase_intent_score"],
                    "avg_price": purchase_data["avg_price"],
                    "shopping_results": purchase_data["shopping_results"],
                    "estimated_conversion_rate": round(conversion_rate, 4),
                    "estimated_monthly_buyers": monthly_buyers,
                })
                
                time.sleep(1)  # Rate limiting

            except Exception as e:
                logger.error(f"Error analyzing keyword '{keyword}': {e}")
                continue

        df = pd.DataFrame(results)
        
        if df.empty:
            return pd.DataFrame(columns=[
                "keyword", "interest_score", "viability_score", "monthly_searches",
                "purchase_intent_score", "avg_price", "history"
            ])

        return df

    # ==========================================
    # TEMPORAL ANALYSIS
    # ==========================================

    def calculate_temporal_metrics(self, history: List[Dict]) -> Dict:
        """
        Calcula métricas para diferentes ventanas temporales.
        
        Args:
            history: [{"date": "Dec 1-7, 2024", "value": 45}, ...]
        
        Returns:
            {
                "7d": {"avg_interest": 65, "velocity": 1.2, "data_points": 7},
                "1m": {"avg_interest": 58, "velocity": 0.8, "data_points": 30},
                ...
            }
        """
        periods = {
            "7d": 7,
            "1m": 30,
            "3m": 90,
            "6m": 180,
            "12m": 365,
        }
        
        results = {}
        
        for period_name, days in periods.items():
            recent_data = history[-days:] if len(history) >= days else history
            
            if not recent_data:
                continue
            
            values = [d["value"] for d in recent_data]
            
            results[period_name] = {
                "avg_interest": round(np.mean(values), 2),
                "velocity": compute_trend_slope(values),
                "consistency": compute_consistency(values),
                "data_points": len(values),
            }
        
        return results

    # ==========================================
    # FILTERING
    # ==========================================

    def filter_high_velocity_trends(
        self, trend_df: pd.DataFrame, min_interest: int = 20
    ) -> pd.DataFrame:
        """Filter trends to keep only products with sufficient interest."""
        filtered = trend_df[(trend_df["interest_score"] >= min_interest)].copy()
        filtered = filtered.sort_values("velocity", ascending=False)

        logger.info(f"Filtered to {len(filtered)} products (min_interest={min_interest})")
        return filtered


def demo():
    """Demo function to test the enhanced trend detector."""
    detector = TrendDetector(geo="US", timeframe="today 3-m")

    print("\n=== Today's Trending Searches ===")
    trending = detector.get_daily_trending_searches(limit=5)
    for i, keyword in enumerate(trending, 1):
        print(f"{i}. {keyword}")

    print("\n=== Analyzing Specific Keywords ===")
    test_keywords = [
        "bluetooth headphones",
        "yoga mat",
        "phone case",
    ]

    interest_df = detector.get_interest_over_time(test_keywords)
    print("\n", interest_df[["keyword", "monthly_searches", "purchase_intent_score", "avg_price"]])


if __name__ == "__main__":
    demo()