import sys
import argparse
import pandas as pd
from typing import List

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
    """

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = load_config(config_path)

        log_path = self.config.get("output", {}).get("log_path", "logs/scraper.log")
        setup_logging(log_path)

        trends_config = self.config.get("trends", {})
        self.trend_detector = TrendDetector(
            geo=trends_config.get("geo", "US"),
            timeframe="today 3-m",
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

    def run_pipeline(self, keywords: List[str] = None, use_trending: bool = False) -> pd.DataFrame:
        """
        Ejecuta el flujo completo: Detección -> Extracción -> Análisis.
        """
        # 1. Obtener Keywords (si no se proporcionan, buscar tendencias o usar default)
        if not keywords:
            if use_trending:
                console.print("[bold blue]Fetching trending searches...[/bold blue]")
                keywords = self.trend_detector.get_daily_trending_searches()
            else:
                keywords = self._get_default_keywords()

        if not keywords:
            console.print("[red]No keywords found to analyze.[/red]")
            return pd.DataFrame()

        # 2. Fase de Detección de Demanda (Genera la columna 'history')
        console.print(f"[bold green]Analyzing demand for: {', '.join(keywords)}[/bold green]")
        interest_df = self.trend_detector.get_interest_over_time(keywords)
        
        if interest_df.empty:
            console.print("[yellow]No trend data available for these keywords.[/yellow]")
            return pd.DataFrame()

        # 3. Fase de Verificación de Suministro (Marketplace Scraper)
        console.print("[bold green]Checking marketplace supply...[/bold green]")
        supply_data = []
        for kw in interest_df["keyword"]:
            # Obtenemos métricas de Amazon y eBay
            metrics = self.scraper.get_supply_metrics(kw)
            supply_data.append(metrics)
        
        supply_df = pd.DataFrame(supply_data)

        # Unimos los datos de interés (que trae 'history') con los de suministro
        combined_df = pd.merge(interest_df, supply_df, on="keyword")

        # Ahora el analyzer calculará el score y generará el reporte
        report_df = self.analyzer.generate_report(combined_df)

        # 6. Guardar y Retornar
        if not report_df.empty:
            output_path = self.config.get("output", {}).get("csv_path", "data/output/report.csv")
            self.analyzer.save_report(report_df, output_path)
            
            console.print(
                Panel(
                    f"[green]Pipeline completed successfully[/green]\nResults for {len(report_df)} products.",
                    border_style="green",
                )
            )
        
        return report_df

    def _get_default_keywords(self) -> List[str]:
        return ["board games"]


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="TrendArbitrage: Discover profitable dropshipping niches"
    )

    parser.add_argument("--keywords", type=str)
    parser.add_argument("--trending", action="store_true")
    parser.add_argument("--config", type=str, default="config/config.yaml")

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

        report_df = engine.run_pipeline(keywords=keywords, use_trending=args.trending)

        if not report_df.empty:
            print_results_summary(report_df, top_n=3)
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
