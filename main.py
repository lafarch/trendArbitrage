import sys
import argparse
import pandas as pd
from typing import List, Dict

from rich.console import Console
from rich.panel import Panel

# Import our custom modules
from src.trend_detector import TrendDetector
from src.marketplace_scraper import MarketplaceScraper
from src.opportunity_analyzer import OpportunityAnalyzer
from src.utils import (
    load_config,
    setup_logging,
    create_directories,
    get_timestamp,
    print_banner,
    print_results_summary,
)

console = Console()


class TrendArbitrageEngine:
    """
    Main orchestrator for the TrendArbitrage system.

    Pipeline:
    1. Detect trends (Google Trends + Shopping data)
    2. Scrape supply (Amazon, eBay, etc.)
    3. Calculate opportunity scores (0-100)
    4. Generate reports with detailed verdicts
    """

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = load_config(config_path)

        log_path = self.config.get("output", {}).get("log_path", "logs/scraper.log")
        setup_logging(log_path)

        trends_config = self.config.get("trends", {})
        self.trend_detector = TrendDetector(
            geo=trends_config.get("geo", "US"),
            timeframe="today 12-m",  # Siempre 12 meses para análisis temporal
        )

        scraping_config = self.config.get("scraping", {})
        self.scraper = MarketplaceScraper(
            delay=scraping_config.get("delay_between_requests", 3),
            max_retries=scraping_config.get("max_retries", 3),
        )

        scoring_config = self.config.get("scoring", {})
        self.analyzer = OpportunityAnalyzer(
            min_interest=scoring_config.get("min_interest_score", 20),
            max_supply=scoring_config.get("max_supply_count", 500),
        )

        console.print(
            Panel(
                "[green]TrendArbitrage Engine initialized successfully[/green]",
                border_style="green",
            )
        )

    def run_pipeline(
        self,
        keywords: List[str] = None,
        use_trending: bool = False,
        temporal_analysis: bool = False,
        platforms: List[str] = ["amazon"],
    ) -> pd.DataFrame:
        """
        Ejecuta el flujo completo: Detección -> Extracción -> Análisis.

        Args:
            keywords: Lista de keywords a analizar
            use_trending: Si True, usa trending searches de Google
            temporal_analysis: Si True, genera análisis temporal
            platforms: Lista de plataformas donde buscar (amazon, ebay, etc.)

        Returns:
            DataFrame con opportunity scores y verdicts
        """

        # ==========================================
        # PASO 1: Obtener Keywords
        # ==========================================
        if not keywords:
            if use_trending:
                console.print("[bold blue]Fetching trending searches...[/bold blue]")
                keywords = self.trend_detector.get_daily_trending_searches()
            else:
                keywords = self._get_default_keywords()

        if not keywords:
            console.print("[red]No keywords found to analyze.[/red]")
            return pd.DataFrame()

        # ==========================================
        # PASO 2: Análisis de Demanda (Trends + Shopping)
        # ==========================================
        console.print(
            f"[bold green]Analyzing demand for: {', '.join(keywords)}[/bold green]"
        )
        interest_df = self.trend_detector.get_interest_over_time(keywords)

        if interest_df.empty:
            console.print(
                "[yellow]No trend data available for these keywords.[/yellow]"
            )
            return pd.DataFrame()

        console.print(
            f"[green]✓ Demand data collected for {len(interest_df)} keywords[/green]"
        )

        # ==========================================
        # PASO 3: Verificación de Suministro (Marketplaces)
        # ==========================================
        console.print(
            f"[bold green]Checking supply on: {', '.join(platforms)}...[/bold green]"
        )
        supply_data = []

        for kw in interest_df["keyword"]:
            metrics = self.scraper.get_supply_metrics(kw, platforms=platforms)
            supply_data.append(metrics)

        supply_df = pd.DataFrame(supply_data)

        # ==========================================
        # PASO 4: Unir Datos
        # ==========================================
        combined_df = pd.merge(interest_df, supply_df, on="keyword")

        console.print(
            f"[green]✓ Combined demand + supply data for {len(combined_df)} keywords[/green]"
        )

        # ==========================================
        # PASO 5: Calcular Opportunity Scores
        # ==========================================
        console.print("[bold blue]Calculating opportunity scores...[/bold blue]")
        report_df = self.analyzer.generate_report(combined_df)

        # ==========================================
        # PASO 6: Análisis Temporal (Opcional)
        # ==========================================
        if temporal_analysis and not report_df.empty:
            console.print(
                "[bold blue]Generating temporal analysis (7d, 1m, 3m, 6m, 12m)...[/bold blue]"
            )

            temporal_reports = []

            for _, row in report_df.iterrows():
                temporal_scores = self.analyzer.calculate_temporal_scores(
                    keyword=row["keyword"],
                    history=row.get("history", []),
                    purchase_intent=row["purchase_intent_score"],
                    total_supply=row["total_supply"],
                    baseline_monthly_searches=row["monthly_searches"],
                )

                temporal_reports.append(
                    {
                        "keyword": row["keyword"],
                        "temporal_scores": temporal_scores,
                    }
                )

            # Guardar análisis temporal
            temporal_path = self.config.get("output", {}).get(
                "temporal_path", "data/output/temporal_analysis.csv"
            )
            self._save_temporal_analysis(temporal_reports, temporal_path)

        # ==========================================
        # PASO 7: Guardar y Retornar
        # ==========================================
        if not report_df.empty:
            # 1. Guardar CSV Estándar (Reporte general)
            output_path = self.config.get("output", {}).get(
                "csv_path", "data/output/report.csv"
            )
            self.analyzer.save_report(report_df, output_path)

            # 2. Generar JSONs para Frontend (Simulación Matemática)
            import json
            import os

            # Crear directorio si no existe
            frontend_dir = "data/frontend"
            os.makedirs(frontend_dir, exist_ok=True)

            console.print(
                f"[bold blue]Generando {len(report_df)} archivos de simulación histórica en: {frontend_dir}/ ...[/bold blue]"
            )

            for _, row in report_df.iterrows():
                try:
                    # Generar datos usando la simulación matemática simple
                    frontend_data = self.analyzer.generate_frontend_json(row)

                    # Guardar archivo: data/frontend/keyword_ejemplo.json
                    safe_filename = (
                        row["keyword"].replace(" ", "_").replace("/", "-").lower()
                    )
                    json_path = os.path.join(frontend_dir, f"{safe_filename}.json")

                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(frontend_data, f, indent=2, ensure_ascii=False)

                except Exception as e:
                    console.print(
                        f"[red]Error generando JSON para {row['keyword']}: {e}[/red]"
                    )

            console.print(
                Panel(
                    f"[green]Pipeline completed successfully[/green]\n"
                    f"Results for {len(report_df)} products.\n"
                    f"Frontend data saved to 'data/frontend/'",
                    border_style="green",
                )
            )

        return report_df

    def _get_default_keywords(self) -> List[str]:
        """Keywords por defecto si no se proporcionan."""
        return ["bluetooth headphones"]

    def _save_temporal_analysis(self, temporal_reports: List[Dict], filepath: str):
        """Guarda análisis temporal en formato legible."""
        rows = []

        for report in temporal_reports:
            keyword = report["keyword"]
            for period, data in report["temporal_scores"].items():
                rows.append(
                    {
                        "keyword": keyword,
                        "period": period,
                        "score": data["score"],
                        "demand_signal": data["demand_signal"],
                        "monthly_searches": data["monthly_searches"],
                        "competition_level": data["competition_level"],
                        "supply_pressure": data["supply_pressure"],
                        "base_ratio": data["base_ratio"],
                        "momentum_multiplier": data["momentum_multiplier"],
                        "trend_velocity": data["trend_velocity"],
                        "data_points": data["data_points"],
                    }
                )

        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False)
        console.print(f"[green]✓ Temporal analysis saved to {filepath}[/green]")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="TrendArbitrage: Discover profitable dropshipping niches"
    )

    parser.add_argument(
        "--keywords",
        type=str,
        help="Comma-separated keywords to analyze (e.g., 'phone case,yoga mat')",
    )
    parser.add_argument(
        "--trending",
        action="store_true",
        help="Use today's trending searches from Google",
    )
    parser.add_argument(
        "--temporal",
        action="store_true",
        help="Generate temporal analysis (7d, 1m, 3m, 6m, 12m)",
    )
    parser.add_argument(
        "--config", type=str, default="config/config.yaml", help="Path to config file"
    )

    return parser.parse_args()


def main():
    args = parse_arguments()
    create_directories()
    print_banner()

    try:
        engine = TrendArbitrageEngine(config_path=args.config)

        keywords = (
            [kw.strip() for kw in args.keywords.split(",")] if args.keywords else None
        )

        report_df = engine.run_pipeline(
            keywords=keywords,
            use_trending=args.trending,
            temporal_analysis=args.temporal,
        )

        if not report_df.empty:
            print_results_summary(report_df, top_n=3)

            # Imprimir verdicts detallados
            console.print("\n[bold cyan]═══ DETAILED VERDICTS ═══[/bold cyan]\n")
            for idx, row in report_df.head(3).iterrows():
                console.print(f"[bold]{row['rank']}. {row['keyword']}[/bold]")
                console.print(row["verdict"])
                console.print("")
        else:
            console.print("[yellow]No viable opportunities found[/yellow]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Pipeline interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise


if __name__ == "__main__":
    main()
