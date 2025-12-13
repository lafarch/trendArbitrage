"""
Utility Functions Module
=========================
Helper functions used across the project.
"""

import yaml
import logging
import os
from datetime import datetime
from typing import Dict, Any


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        logging.warning(f"Config file not found: {config_path}. Using defaults.")
        return {}


def setup_logging(log_path: str = "logs/scraper.log", level=logging.INFO):
    """
    Configure logging for the entire application.
    
    Args:
        log_path: Path to log file
        level: Logging level
    """
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()  # Also print to console
        ]
    )


def create_directories():
    """
    Create necessary project directories if they don't exist.
    """
    directories = [
        'data/raw',
        'data/processed',
        'data/output',
        'logs',
        'config'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def get_timestamp() -> str:
    """
    Get current timestamp as string for file naming.
    
    Returns:
        Timestamp string (YYYYMMDD_HHMMSS)
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def print_banner():
    """
    Print a nice banner for the application.
    """
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║            🎯 TrendArbitrage v1.0                        ║
    ║     AI-Powered Dropshipping Niche Discovery Engine       ║
    ║                                                           ║
    ║  📈 Trend Detection → 🔍 Supply Analysis → 💰 Profit     ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_results_summary(report_df, top_n: int = 3):
    """
    Print a formatted summary of top opportunities.
    
    Args:
        report_df: Report DataFrame from OpportunityAnalyzer
        top_n: Number of top results to display
    """
    print("\n" + "="*70)
    print(f"🏆 TOP {top_n} DROPSHIPPING OPPORTUNITIES")
    print("="*70 + "\n")
    
    for idx, row in report_df.head(top_n).iterrows():
        print(f"#{row['rank']} {row['recommendation']}")
        print(f"   Keyword: {row['keyword']}")
        print(f"   📊 Interest Score: {row['interest_score']}/100")
        print(f"   📦 Supply Count: {row['total_supply']} products")
        print(f"   ⚡ Opportunity Score: {row['opportunity_score']:.4f}")
        print(f"   🏪 Market Status: {row['market_status']}")
        print()
    
    print("="*70)