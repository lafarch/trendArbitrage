"""
Phase 4: Opportunity Analyzer Module (Economic Reality Version)
===============================================================
Purpose: Calculate economically-sensible Opportunity Scores (0-100)

Key Innovation:
- Opportunity Score based on MONETIZED demand vs log-scaled supply
- Multi-timeframe analysis (7d, 1m, 3m, 6m, 12m)
- Detailed verdicts explaining WHY a product is good/bad
- Scores from 0 (avoid) to 100 (gold mine)
"""

import pandas as pd
import logging
import numpy as np
import math
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def compute_trend_slope(values: list) -> float:
    """Calcula la pendiente de crecimiento."""
    if len(values) < 2:
        return 0.0
    x = np.arange(len(values))
    slope = np.polyfit(x, values, 1)[0]
    return round(float(slope), 3)


class OpportunityAnalyzer:
    """
    Combines demand and supply data to identify profitable niches
    with economically-grounded opportunity scores.
    """

    def __init__(self, min_interest: int = 20, max_supply: int = 500):
        self.min_interest = min_interest
        self.max_supply = max_supply
        logger.info(
            f"OpportunityAnalyzer initialized (min_interest={min_interest}, max_supply={max_supply})"
        )

    # ==========================================
    # CORE SCORING ALGORITHM
    # ==========================================

    def calculate_opportunity_score(
        self,
        monthly_searches: int,
        purchase_intent: float,
        conversion_rate: float,
        total_supply: int,
        avg_price: float,
        trend_velocity: float,
    ) -> Dict:
        """
        Opportunity Score = f(Demanda Monetizada, Intención, Saturación, Momentum)
        
        FÓRMULA:
        --------
        1. Demanda Monetizada = (monthly_searches × conversion_rate × avg_price)
           → Ingreso potencial mensual
        
        2. Supply Pressure = log₁₀(total_supply + 10)
           → Competencia en escala logarítmica
        
        3. Base Score = (Demanda Monetizada / Supply Pressure) / 100
           → Normalizado a escala 0-60
        
        4. Bonuses:
           + Purchase Intent Bonus (0-20 pts): Intención de compra alta
           + Momentum Bonus (0-20 pts): Crecimiento acelerado
        
        5. Penalizaciones:
           - Saturation Penalty (0-30 pts): Mercado sobresaturado
        
        RESULTADO: 0-100 donde 100 = mina de oro
        
        Ejemplos:
        ---------
        Caso 1: 10,000 búsquedas/mes, 2% conv, $25 precio, 100 ofertas
          → Revenue: $5,000/mes
          → Pressure: log₁₀(110) = 2.04
          → Base: min(60, 5000/2.04/100) = 24.5
          → Intent: 70/100 * 20 = 14
          → Momentum: 1.5 * 5 = 7.5
          → Penalty: 0 (bajo supply)
          → SCORE: 46 ✅ (Oportunidad sólida)
        
        Caso 2: 5,000 búsquedas/mes, 1% conv, $20 precio, 10,000 ofertas
          → Revenue: $1,000/mes
          → Pressure: log₁₀(10010) = 4.0
          → Base: min(60, 1000/4.0/100) = 2.5
          → Intent: 30/100 * 20 = 6
          → Momentum: 0
          → Penalty: -30 (alta saturación)
          → SCORE: 0 ❌ (Evitar)
        """
        
        # PASO 1: Calcular demanda monetizada mensual
        potential_revenue = monthly_searches * conversion_rate * avg_price
        
        # PASO 2: Presión de competencia (log scale)
        # log₁₀(10) = 1.0, log₁₀(100) = 2.0, log₁₀(1000) = 3.0, log₁₀(10000) = 4.0
        supply_pressure = math.log10(total_supply + 10)
        
        # PASO 3: Score base (normalizado a 0-60)
        if supply_pressure > 0 and potential_revenue > 0:
            base_score = min(60, (potential_revenue / supply_pressure) / 100)
        else:
            base_score = 0
        
        # PASO 4: Bonus por intención de compra (0-20 pts)
        intent_bonus = (purchase_intent / 100) * 20
        
        # PASO 5: Bonus por momentum (0-20 pts)
        momentum_bonus = 0
        if trend_velocity > 1.0:
            momentum_bonus = min(20, trend_velocity * 5)
        elif trend_velocity > 0.5:
            momentum_bonus = 10
        elif trend_velocity > 0:
            momentum_bonus = 5
        
        # PASO 6: Penalización por saturación
        saturation_penalty = 0
        if total_supply > 10000:
            saturation_penalty = 30
        elif total_supply > 5000:
            saturation_penalty = 20
        elif total_supply > 2000:
            saturation_penalty = 10
        
        # SCORE FINAL (0-100)
        final_score = base_score + intent_bonus + momentum_bonus - saturation_penalty
        final_score = max(0, min(100, final_score))
        
        # ANÁLISIS DE FACTORES
        return {
            "score": round(final_score, 1),
            "potential_monthly_revenue": round(potential_revenue, 2),
            "monthly_purchases": round(monthly_searches * conversion_rate, 0),
            "competition_level": self._classify_competition(total_supply),
            "supply_pressure": round(supply_pressure, 2),
            "breakdown": {
                "base_score": round(base_score, 1),
                "intent_bonus": round(intent_bonus, 1),
                "momentum_bonus": round(momentum_bonus, 1),
                "saturation_penalty": round(saturation_penalty, 1),
            },
        }

    def _classify_competition(self, supply: int) -> str:
        """Clasifica nivel de competencia."""
        if supply < 100:
            return "BLUE OCEAN 🌊"
        elif supply < 500:
            return "LOW 🟢"
        elif supply < 2000:
            return "MODERATE 🟡"
        elif supply < 10000:
            return "HIGH 🟠"
        else:
            return "EXTREME 🔴"

    # ==========================================
    # VERDICT GENERATION
    # ==========================================

    def generate_verdict(
        self,
        score: float,
        revenue: float,
        supply: int,
        velocity: float,
        purchase_intent: float,
        breakdown: Dict,
    ) -> str:
        """
        Genera veredicto detallado explicando los factores matemáticos.
        
        El veredicto explica:
        - Por qué el score es alto/bajo
        - Qué factor dominante afecta la decisión
        - Ratio demanda/oferta
        """
        
        # Calcular ratios para análisis
        supply_pressure = math.log10(supply + 10)
        demand_supply_ratio = revenue / (supply + 1)
        
        if score >= 80:
            return (
                f"🚀 MINA DE ORO ({score:.1f}/100)\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Potencial mensual: ${revenue:,.0f}\n"
                f"Competencia: {supply:,} ofertas ({self._classify_competition(supply)})\n"
                f"Ratio D/O: {demand_supply_ratio:.2f} (EXCELENTE)\n"
                f"Momentum: {'🔥 Creciendo rápido' if velocity > 0.5 else '📈 Estable'}\n"
                f"\n💎 Por qué es oro:\n"
                f"  • Base Score: {breakdown['base_score']:.1f}/60 (demanda fuerte)\n"
                f"  • Intent Bonus: +{breakdown['intent_bonus']:.1f} (compran activamente)\n"
                f"  • Momentum: +{breakdown['momentum_bonus']:.1f} (tendencia alcista)\n"
                f"  • Penalización: -{breakdown['saturation_penalty']:.1f} (baja saturación)\n"
                f"\n→ ACTUAR RÁPIDO. Alta demanda + baja competencia."
            )
        
        elif score >= 60:
            return (
                f"💡 OPORTUNIDAD SÓLIDA ({score:.1f}/100)\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Potencial mensual: ${revenue:,.0f}\n"
                f"Competencia: {supply:,} ofertas ({self._classify_competition(supply)})\n"
                f"Ratio D/O: {demand_supply_ratio:.2f} (BUENO)\n"
                f"\n✅ Análisis:\n"
                f"  • Base Score: {breakdown['base_score']:.1f}/60\n"
                f"  • Intent Bonus: +{breakdown['intent_bonus']:.1f}\n"
                f"  • Momentum: +{breakdown['momentum_bonus']:.1f}\n"
                f"  • Penalización: -{breakdown['saturation_penalty']:.1f}\n"
                f"\n→ VIABLE con buena ejecución. Requiere diferenciación."
            )
        
        elif score >= 40:
            # Identificar problema principal
            main_issue = "Mercado saturado" if supply > 2000 else "Demanda insuficiente"
            
            return (
                f"⚠️ RIESGOSO ({score:.1f}/100)\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Potencial mensual: ${revenue:,.0f}\n"
                f"Competencia: {supply:,} ofertas ({self._classify_competition(supply)})\n"
                f"Ratio D/O: {demand_supply_ratio:.4f} (BAJO)\n"
                f"\n⚠️ Problema principal: {main_issue}\n"
                f"  • Base Score: {breakdown['base_score']:.1f}/60 {'⚠️' if breakdown['base_score'] < 20 else ''}\n"
                f"  • Intent Bonus: +{breakdown['intent_bonus']:.1f} {'⚠️' if breakdown['intent_bonus'] < 10 else ''}\n"
                f"  • Momentum: +{breakdown['momentum_bonus']:.1f} {'⚠️' if breakdown['momentum_bonus'] < 5 else ''}\n"
                f"  • Penalización: -{breakdown['saturation_penalty']:.1f} {'🔴' if breakdown['saturation_penalty'] > 10 else ''}\n"
                f"\n→ Márgenes comprimidos. Solo para expertos con ventaja competitiva."
            )
        
        else:
            # Identificar EL factor más problemático
            if supply > 5000:
                main_issue = f"Extrema saturación ({supply:,} ofertas)"
                detail = f"Supply pressure = log₁₀({supply}) = {supply_pressure:.2f} → Divides tu revenue entre {supply_pressure:.2f}"
            elif revenue < 500:
                main_issue = f"Demanda muy baja (${revenue:.0f}/mes)"
                detail = f"Necesitas 10x más búsquedas o mayor precio promedio"
            else:
                main_issue = "Ratio demanda/oferta pésimo"
                detail = f"Ratio actual: {demand_supply_ratio:.4f} (necesitas >0.1 mínimo)"
            
            return (
                f"❌ EVITAR ({score:.1f}/100)\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Potencial mensual: ${revenue:,.0f} 🔴\n"
                f"Competencia: {supply:,} ofertas 🔴\n"
                f"Ratio D/O: {demand_supply_ratio:.6f} (PÉSIMO)\n"
                f"\n🚫 Por qué evitar:\n"
                f"  • Base Score: {breakdown['base_score']:.1f}/60 🔴\n"
                f"  • Intent Bonus: +{breakdown['intent_bonus']:.1f}\n"
                f"  • Momentum: +{breakdown['momentum_bonus']:.1f}\n"
                f"  • Penalización: -{breakdown['saturation_penalty']:.1f} 🔴\n"
                f"\n💀 Problema crítico: {main_issue}\n"
                f"   {detail}\n"
                f"\n→ Pérdida de tiempo y dinero garantizada."
            )

    # ==========================================
    # TEMPORAL ANALYSIS
    # ==========================================

    def calculate_temporal_scores(
        self,
        keyword: str,
        history: List[Dict],
        purchase_intent: float,
        conversion_rate: float,
        avg_price: float,
        total_supply: int,
        baseline_monthly_searches: int,
    ) -> Dict:
        """
        Calcula opportunity scores para múltiples ventanas temporales.
        
        Esto permite ver cómo el score evoluciona con más datos históricos.
        
        Args:
            history: [{"date": "Dec 1-7, 2024", "value": 45}, ...]
            baseline_monthly_searches: Búsquedas mensuales del período completo
        
        Returns:
            {
                "7d": {"score": 72, "searches": 2300, "verdict": "..."},
                "1m": {"score": 68, "searches": 10000, "verdict": "..."},
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
            # Filtrar datos históricos por período
            recent_data = history[-days:] if len(history) >= days else history
            
            if not recent_data:
                continue
            
            # Calcular búsquedas para este período (proporcional)
            period_searches = int(baseline_monthly_searches * (days / 30))
            
            # Calcular velocidad de crecimiento en este período
            values = [d["value"] for d in recent_data]
            trend_velocity = compute_trend_slope(values)
            
            # Calcular opportunity score
            score_data = self.calculate_opportunity_score(
                monthly_searches=baseline_monthly_searches,  # Mantenemos base mensual
                purchase_intent=purchase_intent,
                conversion_rate=conversion_rate,
                total_supply=total_supply,
                avg_price=avg_price,
                trend_velocity=trend_velocity,
            )
            
            # Generar veredicto
            verdict = self.generate_verdict(
                score=score_data["score"],
                revenue=score_data["potential_monthly_revenue"],
                supply=total_supply,
                velocity=trend_velocity,
                purchase_intent=purchase_intent,
                breakdown=score_data["breakdown"],
            )
            
            results[period_name] = {
                **score_data,
                "period": period_name,
                "period_searches": period_searches,
                "trend_velocity": round(trend_velocity, 3),
                "data_points": len(values),
                "verdict": verdict,
            }
        
        return results

    # ==========================================
    # REPORT GENERATION
    # ==========================================

    def generate_report(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """
        Genera reporte final con opportunity scores y clasificaciones.
        
        Input DataFrame debe tener:
        - keyword, monthly_searches, purchase_intent_score, avg_price
        - estimated_conversion_rate, total_supply, velocity, history
        """
        
        if df.empty:
            logger.warning("Empty dataframe provided to generate_report")
            return pd.DataFrame()
        
        opportunities = []
        
        for _, row in df.iterrows():
            # Calcular opportunity score
            score_data = self.calculate_opportunity_score(
                monthly_searches=row.get("monthly_searches", 0),
                purchase_intent=row.get("purchase_intent_score", 0),
                conversion_rate=row.get("estimated_conversion_rate", 0.01),
                total_supply=row.get("total_supply", 0),
                avg_price=row.get("avg_price", 0),
                trend_velocity=row.get("velocity", 0),
            )
            
            # Generar veredicto
            verdict = self.generate_verdict(
                score=score_data["score"],
                revenue=score_data["potential_monthly_revenue"],
                supply=row.get("total_supply", 0),
                velocity=row.get("velocity", 0),
                purchase_intent=row.get("purchase_intent_score", 0),
                breakdown=score_data["breakdown"],
            )
            
            # Compilar resultado
            opportunities.append({
                "keyword": row["keyword"],
                "opportunity_score": score_data["score"],
                "potential_monthly_revenue": score_data["potential_monthly_revenue"],
                "monthly_searches": row.get("monthly_searches", 0),
                "monthly_purchases": score_data["monthly_purchases"],
                "purchase_intent_score": row.get("purchase_intent_score", 0),
                "avg_price": row.get("avg_price", 0),
                "total_supply": row.get("total_supply", 0),
                "competition_level": score_data["competition_level"],
                "supply_pressure": score_data["supply_pressure"],
                "trend_velocity": row.get("velocity", 0),
                "is_rising": row.get("is_rising", False),
                "verdict": verdict,
                "history": row.get("history", []),
                # Breakdown para análisis detallado
                "base_score": score_data["breakdown"]["base_score"],
                "intent_bonus": score_data["breakdown"]["intent_bonus"],
                "momentum_bonus": score_data["breakdown"]["momentum_bonus"],
                "saturation_penalty": score_data["breakdown"]["saturation_penalty"],
            })
        
        report = pd.DataFrame(opportunities)
        
        # Ordenar por opportunity score (descendente)
        report = report.sort_values("opportunity_score", ascending=False)
        
        # Limitar a top_n
        report = report.head(top_n)
        
        # Agregar ranking
        if not report.empty:
            report.insert(0, "rank", range(1, len(report) + 1))
        
        logger.info(f"Generated report with {len(report)} opportunities")
        return report

    def save_report(self, df: pd.DataFrame, filepath: str):
        """Guarda el reporte en CSV."""
        df.to_csv(filepath, index=False)
        logger.info(f"Report saved to {filepath}")
        print(f"\n✅ Report saved: {filepath}")