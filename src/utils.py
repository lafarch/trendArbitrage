"""
Utility Functions Module (Enhanced)
===================================
Improved terminal output, logging clarity, and demand-aware summaries.
"""

import yaml
import logging
import os
from datetime import datetime
from typing import Dict, Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()


# ------------------------------------------------------------------
# Config & setup
# ------------------------------------------------------------------

def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logging.warning(f"Config file not found: {config_path}. Using defaults.")
        return {}


def setup_logging(log_path: str = "logs/scraper.log", level=logging.INFO):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ],
    )


def create_directories():
    for directory in [
        "data/raw",
        "data/processed",
        "data/output",
        "logs",
        "config",
    ]:
        os.makedirs(directory, exist_ok=True)


def get_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# ------------------------------------------------------------------
# UI / Presentation
# ------------------------------------------------------------------

def print_banner():
    console.print(
        Panel.fit(
            "[bold cyan]TrendArbitrage[/bold cyan]\n"
            "[white]Niche Discovery Engine[/white]\n\n"
            "[green]Demand → Supply → Opportunity[/green]",
            border_style="cyan",
        )
    )


def _explain_opportunity(row) -> str:
    reasons = []

    demand = row.get("viability_score", 0)
    supply = row.get("total_supply", 0)

    # Demand analysis
    if demand >= 80:
        reasons.append("strong demand")
    elif demand >= 50:
        reasons.append("moderate demand")
    else:
        reasons.append("weak demand")

    # Supply analysis
    if supply >= 1000:
        reasons.append("high competition")
    elif supply >= 500:
        reasons.append("moderate competition")
    else:
        reasons.append("low competition")

    # Trend behavior
    if row.get("recent_spike"):
        reasons.append("recent interest spike")
    elif row.get("trend_slope", 0) > 0:
        reasons.append("steady upward trend")

    return ", ".join(reasons)


def print_results_summary(report_df, top_n: int = 3):
    console.print("\n[bold]Top Opportunities Overview[/bold]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Rank", justify="right")
    table.add_column("Keyword", style="cyan")
    table.add_column("Demand", justify="right")
    table.add_column("Supply", justify="right")
    table.add_column("Opp. Score", justify="right")
    table.add_column("Recommendation")
    table.add_column("Why")

    for _, row in report_df.head(top_n).iterrows():
        demand_value = (
            row["viability_score"]
            if "viability_score" in row
            else row.get("interest_score", 0)
        )

        table.add_row(
            str(row["rank"]),
            row["keyword"],
            f"{demand_value:.0f}",
            str(row["total_supply"]),
            f"{row['opportunity_score']:.2f}",
            row["recommendation"],
            _explain_opportunity(row)
,
        )

    console.print(table)
    console.print("\n")


# ------------------------------------------------------------------
# End of file
# ------------------------------------------------------------------
