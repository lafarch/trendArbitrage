"""
Utility Functions for TrendArbitrage
====================================
Includes: Config loading, logging, directory creation, and result display
"""

import os
import yaml
import logging
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import pandas as pd

console = Console()


def load_config(config_path: str = "config/config.yaml") -> dict:
    """Load configuration from YAML file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    return config


def setup_logging(log_path: str = "logs/scraper.log"):
    """Setup logging configuration."""
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler(),
        ],
    )


def create_directories():
    """Create necessary directories for the project."""
    directories = [
        "data/output",
        "logs",
        "config",
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def get_timestamp() -> str:
    """Get current timestamp as string."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def print_banner():
    """Print application banner."""
    banner = """
╭───────────────────────────────╮
│ TrendArbitrage                │
│ Niche Discovery Engine        │
│                               │
│ Demand → Supply → Opportunity │
╰───────────────────────────────╯
    """
    print(banner)


def print_results_summary(df: pd.DataFrame, top_n: int = 5):
    """
    Print summary table of top opportunities (simplified schema).
    
    New schema:
    - opportunity_score (0-100)
    - demand_signal (qualified searches)
    - competition_level
    - base_ratio (demand/supply)
    - momentum_multiplier
    """
    if df.empty:
        console.print("[yellow]No results to display[/yellow]")
        return

    console.print("\n[bold cyan]Top Opportunities Overview[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Rank", style="dim", width=6)
    table.add_column("Keyword", style="cyan", width=25)
    table.add_column("Score", justify="right", style="green", width=8)
    table.add_column("Demand", justify="right", style="yellow", width=12)
    table.add_column("Supply", justify="right", width=12)
    table.add_column("Competition", width=18)
    table.add_column("Status", width=20)

    for idx, row in df.head(top_n).iterrows():
        # Determinar status basado en opportunity_score
        score = row.get("opportunity_score", 0)
        
        if score >= 70:
            status = "🚀 EXCELENTE"
            status_style = "bold green"
        elif score >= 50:
            status = "💡 VIABLE"
            status_style = "green"
        elif score >= 30:
            status = "⚠️ RIESGOSO"
            status_style = "yellow"
        else:
            status = "❌ EVITAR"
            status_style = "red"

        table.add_row(
            str(row.get("rank", idx + 1)),
            row["keyword"],
            f"{score:.1f}",
            f"{row.get('demand_signal', 0):,.0f}",
            f"{row.get('total_supply', 0):,}",
            row.get("competition_level", "N/A"),
            status,
        )

    console.print(table)
    
    # Mostrar insights del mejor resultado
    console.print("\n[bold cyan]Key Insights:[/bold cyan]")
    
    best = df.iloc[0]
    console.print(
        f"• Best opportunity: [bold]{best['keyword']}[/bold] "
        f"(Score: {best['opportunity_score']:.1f}/100)"
    )
    console.print(
        f"• Demand signal: [green]{best['demand_signal']:,.0f} qualified searches/month[/green]"
    )
    console.print(
        f"• Competition: {best['competition_level']} "
        f"({best['total_supply']:,} listings, pressure {best['supply_pressure']:.2f})"
    )
    console.print(
        f"• Ratio D/S: {best['base_ratio']:.1f}"
    )
    
    momentum = best.get('momentum_multiplier', 1.0)
    if momentum > 1.3:
        console.print(f"• Momentum: [green]🔥 Amplifying {momentum:.2f}x[/green]")
    elif momentum > 1.1:
        console.print(f"• Momentum: [blue]📈 Growing {momentum:.2f}x[/blue]")
    else:
        console.print(f"• Momentum: [yellow]📊 Stable {momentum:.2f}x[/yellow]")


def print_detailed_analysis(row: pd.Series):
    """
    Print detailed analysis for a single product (simplified).
    """
    console.print(Panel(
        f"[bold cyan]{row['keyword']}[/bold cyan]\n\n"
        f"[bold]Opportunity Score:[/bold] {row['opportunity_score']:.1f}/100\n\n"
        f"[bold]Demand Metrics:[/bold]\n"
        f"  • Monthly Searches: {row['monthly_searches']:,}\n"
        f"  • Purchase Intent: {row['purchase_intent_score']:.1f}/100\n"
        f"  • Demand Signal: {row['demand_signal']:,.0f} qualified searches\n\n"
        f"[bold]Competition:[/bold]\n"
        f"  • Total Supply: {row['total_supply']:,} listings\n"
        f"  • Level: {row['competition_level']}\n"
        f"  • Supply Pressure: {row['supply_pressure']:.2f}\n\n"
        f"[bold]Scoring:[/bold]\n"
        f"  • Base Ratio (D/S): {row['base_ratio']:.1f}\n"
        f"  • Momentum Multiplier: {row['momentum_multiplier']:.2f}x\n"
        f"  • Trend Velocity: {row['trend_velocity']:.3f}\n"
        f"  • Rising: {'Yes ✅' if row['is_rising'] else 'No ❌'}",
        border_style="cyan",
        title="Detailed Analysis",
    ))
    
    # Print full verdict
    console.print("\n[bold cyan]Full Verdict:[/bold cyan]\n")
    console.print(row['verdict'])


def save_detailed_report(df: pd.DataFrame, filepath: str):
    """
    Save detailed report with all metrics to CSV.
    """
    df.to_csv(filepath, index=False)
    console.print(f"\n[green]✓ Detailed report saved to {filepath}[/green]")


def print_temporal_summary(temporal_df: pd.DataFrame, keyword: str):
    """
    Print summary of temporal analysis for a keyword.
    
    Shows how the opportunity score evolves across different timeframes.
    """
    console.print(f"\n[bold cyan]Temporal Analysis: {keyword}[/bold cyan]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Period", width=10)
    table.add_column("Score", justify="right", style="green", width=8)
    table.add_column("Demand", justify="right", style="yellow", width=12)
    table.add_column("Velocity", justify="right", width=10)
    table.add_column("Momentum", justify="right", width=10)
    table.add_column("Data Pts", justify="right", width=10)
    
    keyword_data = temporal_df[temporal_df["keyword"] == keyword]
    
    for _, row in keyword_data.iterrows():
        table.add_row(
            row["period"],
            f"{row['score']:.1f}",
            f"{row.get('demand_signal', 0):,.0f}",
            f"{row['trend_velocity']:.3f}",
            f"{row.get('momentum_multiplier', 1.0):.2f}x",
            str(row["data_points"]),
        )
    
    console.print(table)
    
    # Insight sobre consistencia
    scores = keyword_data["score"].values
    if len(scores) > 1:
        score_variance = scores.std()
        if score_variance < 5:
            console.print("\n[green]✓ Score consistente en todos los períodos[/green]")
        elif score_variance < 15:
            console.print("\n[yellow]⚠️ Score moderadamente variable[/yellow]")
        else:
            console.print("\n[red]❌ Score muy volátil - datos poco confiables[/red]")