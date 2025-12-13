"""
TrendArbitrage Main Execution Script
=====================================
Orchestrates the entire pipeline:
1. Detect trending keywords (demand)
2. Check marketplace supply
3. Calculate opportunity scores
4. Generate report

Usage:
    python main.py
    
    Or with custom keywords:
    python main.py --keywords "clash royale plush,skibidi toilet toy"
"""

import sys
import argparse
import pandas as pd
from typing import List

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
    print_results_summary
)


class TrendArbitrageEngine:
    """
    Main orchestrator for the TrendArbitrage system.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize the engine with configuration.
        
        Args:
            config_path: Path to YAML configuration file
        """
        # Load config
        self.config = load_config(config_path)
        
        # Setup logging
        log_path = self.config.get('output', {}).get('log_path', 'logs/scraper.log')
        setup_logging(log_path)
        
        # Initialize modules
        trends_config = self.config.get('trends', {})
        self.trend_detector = TrendDetector(
            geo=trends_config.get('geo', 'US'),
            timeframe=trends_config.get('timeframe', 'now 7-d')
        )
        
        scraping_config = self.config.get('scraping', {})
        self.scraper = MarketplaceScraper(
            delay=scraping_config.get('delay_between_requests', 3),
            max_retries=scraping_config.get('max_retries', 3)
        )
        
        scoring_config = self.config.get('scoring', {})
        self.analyzer = OpportunityAnalyzer(
            min_interest=scoring_config.get('min_interest_score', 20),
            max_supply=scoring_config.get('max_supply_count', 500)
        )
        
        print("✅ TrendArbitrage Engine initialized successfully")
    
    def run_pipeline(self, keywords: List[str] = None, use_trending: bool = False) -> pd.DataFrame:
        """
        Execute the full pipeline.
        
        Args:
            keywords: Optional list of keywords to analyze
            use_trending: If True, fetch today's trending searches
            
        Returns:
            DataFrame with opportunity analysis
        """
        print("\n" + "="*70)
        print("🚀 STARTING TRENDARBITRAGE PIPELINE")
        print("="*70 + "\n")
        
        # PHASE 1: Get keywords to analyze
        if use_trending:
            print("📡 Phase 1: Fetching trending searches from Google...")
            keywords = self.trend_detector.get_daily_trending_searches()
            print(f"✅ Found {len(keywords)} trending keywords\n")
        elif keywords is None:
            print("⚠️  No keywords provided. Using default test set...")
            keywords = self._get_default_keywords()
        
        print(f"📋 Analyzing {len(keywords)} keywords:")
        for i, kw in enumerate(keywords[:10], 1):
            print(f"   {i}. {kw}")
        if len(keywords) > 10:
            print(f"   ... and {len(keywords) - 10} more")
        print()
        
        # PHASE 2: Get interest scores (DEMAND)
        print("📈 Phase 2: Analyzing search interest (Demand Detection)...")
        trend_df = self.trend_detector.get_interest_over_time(keywords)
        
        if trend_df.empty:
            print("❌ No trend data retrieved. Exiting.")
            return pd.DataFrame()
        
        print(f"✅ Retrieved interest data for {len(trend_df)} keywords\n")
        
        # PHASE 3: Get supply counts (SUPPLY)
        print("🛒 Phase 3: Checking marketplace supply (Saturation Check)...")
        supply_data = []
        
        for keyword in trend_df['keyword']:
            print(f"   Scraping: {keyword}...")
            supply_metrics = self.scraper.get_supply_metrics(
                keyword,
                platforms=['ebay']  # Can add 'amazon' if needed
            )
            supply_data.append(supply_metrics)
        
        supply_df = pd.DataFrame(supply_data)
        print(f"✅ Retrieved supply data for {len(supply_df)} keywords\n")
        
        # PHASE 4: Calculate opportunity scores
        print("🎯 Phase 4: Calculating Opportunity Scores...")
        scored_df = self.analyzer.merge_and_score(trend_df, supply_df)
        print(f"✅ Calculated scores for {len(scored_df)} products\n")
        
        # PHASE 5: Generate final report
        print("📊 Phase 5: Generating opportunity report...")
        top_n = self.config.get('scoring', {}).get('top_n_results', 10)
        report_df = self.analyzer.generate_report(scored_df, top_n=top_n)
        
        # Save report
        timestamp = get_timestamp()
        output_path = f"data/output/opportunities_{timestamp}.csv"
        self.analyzer.save_report(report_df, output_path)
        
        print("\n" + "="*70)
        print("✅ PIPELINE COMPLETED SUCCESSFULLY")
        print("="*70)
        
        return report_df
    
    def _get_default_keywords(self) -> List[str]:
        """
        Return default test keywords.
        
        These are based on recent viral trends and gaming products.
        """
        return [
            "clash royale plush",
            "skibidi toilet toy",
            "digital circus plush",
            "poppy playtime toy",
            "among us plush",
            "bluey toys",
            "squishmallow rare",
            "pokemon plush",
            "roblox toy",
            "minecraft plush"
        ]


def parse_arguments():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description='TrendArbitrage: Discover profitable dropshipping niches'
    )
    
    parser.add_argument(
        '--keywords',
        type=str,
        help='Comma-separated list of keywords to analyze (e.g., "toy 1,toy 2")'
    )
    
    parser.add_argument(
        '--trending',
        action='store_true',
        help='Use today\'s trending searches instead of custom keywords'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file'
    )
    
    return parser.parse_args()


def main():
    """
    Main entry point for the application.
    """
    # Parse arguments
    args = parse_arguments()
    
    # Create necessary directories
    create_directories()
    
    # Print banner
    print_banner()
    
    try:
        # Initialize engine
        engine = TrendArbitrageEngine(config_path=args.config)
        
        # Prepare keywords
        keywords = None
        if args.keywords:
            keywords = [kw.strip() for kw in args.keywords.split(',')]
        
        # Run pipeline
        report_df = engine.run_pipeline(
            keywords=keywords,
            use_trending=args.trending
        )
        
        # Display results
        if not report_df.empty:
            print_results_summary(report_df, top_n=3)
            
            print("\n💡 Next Steps:")
            print("   1. Research the top products on AliExpress/DHgate for suppliers")
            print("   2. Create engaging short-form video content (TikTok, Instagram Reels)")
            print("   3. Set up a Shopify store or use a dropshipping platform")
            print("   4. Test with small ad budget to validate demand")
            print("   5. Scale winners, kill losers")
            print("\n📂 Full results saved to: data/output/")
            
        else:
            print("\n⚠️  No opportunities found. Try different keywords or time periods.")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()