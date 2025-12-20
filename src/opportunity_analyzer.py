"""
Phase 4: Opportunity Analyzer Module (Simplified & Grounded)
============================================================
Purpose: Calculate honest Opportunity Scores (0-100) without revenue theater

Key Changes:
- Momentum is MULTIPLICATIVE (amplifies demand, not additive)
- No fictional revenue calculations
- Temporal analysis uses ACTUAL period data
- Focus on demand signal vs supply pressure
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
    Combines demand and supply data to identify profitable niches.
    Simplified scoring without revenue theater.
    """

    def __init__(self, min_interest: int = 20, max_supply: int = 500):
        self.min_interest = min_interest
        self.max_supply = max_supply
        logger.info(
            f"OpportunityAnalyzer initialized (min_interest={min_interest})"
        )

    # ==========================================
    # CORE SCORING ALGORITHM (SIMPLIFIED)
    # ==========================================

    def calculate_opportunity_score(
        self,
        monthly_searches: int,
        purchase_intent: float,      # 0-100
        total_supply: int,
        trend_velocity: float,
    ) -> Dict:
        """
        Opportunity Score = (Demand Signal / Supply Pressure) × Momentum × 100
        
        FÓRMULA SIMPLIFICADA:
        ---------------------
        1. Demand Signal = monthly_searches × (purchase_intent / 100)
           → Búsquedas cualificadas por intención de compra
        
        2. Supply Pressure = log₁₀(total_supply + 10)
           → Competencia en escala logarítmica
        
        3. Base Ratio = Demand Signal / Supply Pressure
           → Demanda cualificada por unidad de competencia
        
        4. Momentum Multiplier = 1 + (velocity × 0.5)
           → Amplificador de 1x (velocity=0) a 2x (velocity=2.0)
        
        5. Final Score = (Base Ratio × Momentum Multiplier) / 50
           → Normalizado a escala 0-100
        
        RESULTADO: 0-100 donde 100 = demanda explosiva con baja competencia
        
        Ejemplos:
        ---------
        Caso 1: 10,000 búsquedas, 70% intent, 100 ofertas, velocity 1.5
          → Demand Signal: 10,000 × 0.7 = 7,000
          → Pressure: log₁₀(110) = 2.04
          → Base Ratio: 7,000 / 2.04 = 3,431
          → Momentum: 1 + (1.5 × 0.5) = 1.75x
          → Score: (3,431 × 1.75) / 50 = 120 → capped at 100 ✅
        
        Caso 2: 5,000 búsquedas, 30% intent, 10,000 ofertas, velocity 0.1
          → Demand Signal: 5,000 × 0.3 = 1,500
          → Pressure: log₁₀(10,010) = 4.0
          → Base Ratio: 1,500 / 4.0 = 375
          → Momentum: 1 + (0.1 × 0.5) = 1.05x
          → Score: (375 × 1.05) / 50 = 7.9 ❌
        """
        
        # PASO 1: Calcular demanda cualificada
        demand_signal = monthly_searches * (purchase_intent / 100)
        
        # PASO 2: Presión de competencia (log scale)
        supply_pressure = math.log10(total_supply + 10)
        
        # PASO 3: Ratio base (demanda/competencia)
        if supply_pressure > 0 and demand_signal > 0:
            base_ratio = demand_signal / supply_pressure
        else:
            base_ratio = 0
        
        # PASO 4: Momentum multiplier (1x a 2x)
        momentum_multiplier = 1 + (max(0, trend_velocity) * 0.5)
        momentum_multiplier = min(momentum_multiplier, 2.0)  # Cap at 2x
        
        # PASO 5: Score final (normalizado a 0-100)
        final_score = (base_ratio * momentum_multiplier) / 50
        final_score = max(0, min(100, final_score))
        
        # PASO 6: Penalización adicional por extrema saturación
        saturation_penalty = 0
        if total_supply > 20000:
            saturation_penalty = 15
        elif total_supply > 10000:
            saturation_penalty = 10
        
        final_score = max(0, final_score - saturation_penalty)
        
        # ANÁLISIS DE FACTORES
        return {
            "score": round(final_score, 1),
            "demand_signal": round(demand_signal, 0),
            "supply_pressure": round(supply_pressure, 2),
            "base_ratio": round(base_ratio, 1),
            "momentum_multiplier": round(momentum_multiplier, 2),
            "competition_level": self._classify_competition(total_supply),
            "saturation_penalty": saturation_penalty,
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
    # VERDICT GENERATION (SIMPLIFIED)
    # ==========================================

    def generate_verdict(
        self,
        score: float,
        demand_signal: float,
        supply: int,
        velocity: float,
        purchase_intent: float,
        base_ratio: float,
        momentum_multiplier: float,
    ) -> str:
        """
        Genera veredicto honesto sin teatro financiero.
        """
        
        supply_pressure = math.log10(supply + 10)
        
        if score >= 70:
            return (
                f"🚀 EXCELENTE OPORTUNIDAD ({score:.1f}/100)\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Demanda cualificada: {demand_signal:,.0f} búsquedas/mes\n"
                f"Competencia: {supply:,} ofertas ({self._classify_competition(supply)})\n"
                f"Ratio D/S: {base_ratio:.1f} (EXCELENTE)\n"
                f"Momentum: {momentum_multiplier:.2f}x {'🔥' if momentum_multiplier > 1.3 else '📈'}\n"
                f"\n💎 Por qué es buena:\n"
                f"  • Alta demanda cualificada ({demand_signal:,.0f})\n"
                f"  • Baja presión de competencia ({supply_pressure:.2f})\n"
                f"  • {'Crecimiento acelerado' if velocity > 0.5 else 'Demanda estable'}\n"
                f"\n→ ACTUAR RÁPIDO. Ventana de oportunidad."
            )
        
        elif score >= 50:
            return (
                f"💡 OPORTUNIDAD VIABLE ({score:.1f}/100)\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Demanda cualificada: {demand_signal:,.0f} búsquedas/mes\n"
                f"Competencia: {supply:,} ofertas ({self._classify_competition(supply)})\n"
                f"Ratio D/S: {base_ratio:.1f} (BUENO)\n"
                f"Momentum: {momentum_multiplier:.2f}x\n"
                f"\n✅ Análisis:\n"
                f"  • Demanda suficiente para competir\n"
                f"  • Ratio demanda/competencia favorable\n"
                f"  • Requiere diferenciación fuerte\n"
                f"\n→ VIABLE con ejecución sólida."
            )
        
        elif score >= 30:
            # Identificar problema dominante
            if supply > 5000:
                problem = f"Alta saturación ({supply:,} ofertas)"
            elif demand_signal < 1000:
                problem = f"Demanda baja ({demand_signal:,.0f} búsquedas cualificadas)"
            else:
                problem = f"Ratio D/S insuficiente ({base_ratio:.1f})"
            
            return (
                f"⚠️ RIESGOSO ({score:.1f}/100)\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Demanda cualificada: {demand_signal:,.0f} búsquedas/mes\n"
                f"Competencia: {supply:,} ofertas ({self._classify_competition(supply)})\n"
                f"Ratio D/S: {base_ratio:.1f} (BAJO)\n"
                f"\n⚠️ Problema principal: {problem}\n"
                f"  • Supply pressure: {supply_pressure:.2f}\n"
                f"  • Momentum: {momentum_multiplier:.2f}x {'⚠️' if momentum_multiplier < 1.2 else ''}\n"
                f"\n→ Márgenes comprimidos. Solo para expertos."
            )
        
        else:
            # Diagnóstico crítico
            if supply > 10000:
                critical_issue = f"Extrema saturación ({supply:,} ofertas)"
                explanation = f"Supply pressure {supply_pressure:.2f} divide tu demanda hasta volverla inviable"
            elif demand_signal < 500:
                critical_issue = f"Demanda insuficiente ({demand_signal:,.0f})"
                explanation = f"Necesitas 5-10x más búsquedas o mayor intención de compra"
            else:
                critical_issue = f"Ratio D/S crítico ({base_ratio:.2f})"
                explanation = f"Demanda {demand_signal:,.0f} ÷ Pressure {supply_pressure:.2f} = ratio pésimo"
            
            return (
                f"❌ EVITAR ({score:.1f}/100)\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Demanda cualificada: {demand_signal:,.0f} búsquedas/mes 🔴\n"
                f"Competencia: {supply:,} ofertas 🔴\n"
                f"Ratio D/S: {base_ratio:.2f} (CRÍTICO)\n"
                f"\n💀 Problema crítico: {critical_issue}\n"
                f"   {explanation}\n"
                f"   Momentum: {momentum_multiplier:.2f}x (no salva el ratio base)\n"
                f"\n→ Mercado inviable. Buscar otro nicho."
            )

    # ==========================================
    # TEMPORAL ANALYSIS (FIXED)
    # ==========================================

    def calculate_temporal_scores(
        self,
        keyword: str,
        history: List[Dict],
        purchase_intent: float,
        total_supply: int,
        baseline_monthly_searches: int,
    ) -> Dict:
        """
        Calcula opportunity scores REALES para cada período.
        
        Ahora usa los datos históricos específicos de cada ventana
        en lugar de reutilizar el mismo baseline.
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
            
            # Calcular DEMANDA REAL del período (no baseline)
            values = [d["value"] for d in recent_data]
            avg_interest = np.mean(values)
            
            # Escalar a búsquedas mensuales para este período específico
            # Usamos la función directamente en lugar de importar
            period_monthly_searches = int((avg_interest / 100) * 10000)
            period_monthly_searches = max(period_monthly_searches, 100)
            
            # Calcular velocidad de crecimiento en este período
            trend_velocity = compute_trend_slope(values)
            
            # Calcular opportunity score con datos REALES del período
            score_data = self.calculate_opportunity_score(
                monthly_searches=period_monthly_searches,  # REAL del período
                purchase_intent=purchase_intent,
                total_supply=total_supply,
                trend_velocity=trend_velocity,
            )
            
            # Generar veredicto
            verdict = self.generate_verdict(
                score=score_data["score"],
                demand_signal=score_data["demand_signal"],
                supply=total_supply,
                velocity=trend_velocity,
                purchase_intent=purchase_intent,
                base_ratio=score_data["base_ratio"],
                momentum_multiplier=score_data["momentum_multiplier"],
            )
            
            results[period_name] = {
                **score_data,
                "period": period_name,
                "avg_interest": round(avg_interest, 1),
                "monthly_searches": period_monthly_searches,
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
        Genera reporte con scoring simplificado (sin revenue theater).
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
                total_supply=row.get("total_supply", 0),
                trend_velocity=row.get("velocity", 0),
            )
            
            # Generar veredicto
            verdict = self.generate_verdict(
                score=score_data["score"],
                demand_signal=score_data["demand_signal"],
                supply=row.get("total_supply", 0),
                velocity=row.get("velocity", 0),
                purchase_intent=row.get("purchase_intent_score", 0),
                base_ratio=score_data["base_ratio"],
                momentum_multiplier=score_data["momentum_multiplier"],
            )
            
            # Compilar resultado
            opportunities.append({
                "keyword": row["keyword"],
                "opportunity_score": score_data["score"],
                "demand_signal": score_data["demand_signal"],
                "monthly_searches": row.get("monthly_searches", 0),
                "purchase_intent_score": row.get("purchase_intent_score", 0),
                "total_supply": row.get("total_supply", 0),
                "competition_level": score_data["competition_level"],
                "supply_pressure": score_data["supply_pressure"],
                "base_ratio": score_data["base_ratio"],
                "trend_velocity": row.get("velocity", 0),
                "momentum_multiplier": score_data["momentum_multiplier"],
                "is_rising": row.get("is_rising", False),
                "verdict": verdict,
                "history": row.get("history", []),
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