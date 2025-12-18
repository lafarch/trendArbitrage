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

    def run_pipeline(
        self, keywords: List[str] = None, use_trending: bool = False
    ) -> pd.DataFrame:

        console.print(
            Panel(
                "[bold cyan]Starting TrendArbitrage Pipeline[/bold cyan]", expand=False
            )
        )

        # -------------------- PHASE 1 --------------------
        console.rule("[bold]Phase 1: Keyword Selection[/bold]")

        if use_trending:
            keywords = self.trend_detector.get_daily_trending_searches(limit=20)
            console.print(f"Using {len(keywords)} trending searches")
        elif keywords is None:
            keywords = self._get_default_keywords()
            console.print("Using default test keywords")

        console.print(f"Keywords to analyze: {', '.join(keywords)}")

        # -------------------- PHASE 2 --------------------
        console.rule("[bold]Phase 2: Demand Analysis[/bold]")
        trend_df = self.trend_detector.get_interest_over_time(keywords)

        if trend_df.empty:
            console.print("[red]No demand data retrieved. Aborting.[/red]")
            return pd.DataFrame()

        console.print(f"Demand data collected for {len(trend_df)} keywords")

        # -------------------- PHASE 3 --------------------
        console.rule("[bold]Phase 3: Supply Analysis[/bold]")
        supply_data = []

        for keyword in trend_df["keyword"]:
            console.print(f"Checking supply for: [cyan]{keyword}[/cyan]")
            supply_data.append(
                self.scraper.get_supply_metrics(
                    keyword,
                    platforms=["amazon", "ebay", "walmart", "aliexpress"],
                )
            )

        supply_df = pd.DataFrame(supply_data)
        console.print(f"Supply data collected for {len(supply_df)} keywords")

        # -------------------- PHASE 4 --------------------
        console.rule("[bold]Phase 4: Opportunity Scoring[/bold]")
        scored_df = self.analyzer.merge_and_score(trend_df, supply_df)

        console.print(f"Opportunity scores calculated for {len(scored_df)} items")

        # -------------------- PHASE 5 --------------------
        console.rule("[bold]Phase 5: Reporting[/bold]")
        top_n = self.config.get("scoring", {}).get("top_n_results", 10)
        report_df = self.analyzer.generate_report(scored_df, top_n=top_n)

        timestamp = get_timestamp()
        output_path = f"data/output/opportunities_{timestamp}.csv"
        self.analyzer.save_report(report_df, output_path)

        console.print(
            Panel(
                f"[green]Pipeline completed successfully[/green]\nSaved to {output_path}",
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
