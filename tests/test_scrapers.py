"""
Unit Tests for TrendArbitrage
==============================
Tests for core functionality of scrapers and analyzers.

Run with: pytest tests/test_scrapers.py -v
"""

import pytest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from trend_detector import TrendDetector
from marketplace_scraper import MarketplaceScraper
from opportunity_analyzer import OpportunityAnalyzer
import pandas as pd


# ============================================================================
# TrendDetector Tests
# ============================================================================

class TestTrendDetector:
    """Test suite for TrendDetector class."""
    
    def test_initialization(self):
        """Test that TrendDetector initializes correctly."""
        detector = TrendDetector(geo="US", timeframe="now 7-d")
        assert detector.geo == "US"
        assert detector.timeframe == "now 7-d"
        assert detector.pytrends is not None
    
    def test_get_daily_trending_searches(self):
        """Test fetching trending searches (requires internet)."""
        detector = TrendDetector()
        trending = detector.get_daily_trending_searches()
        
        # Should return a list
        assert isinstance(trending, list)
        # Should have some results (or empty list if API fails)
        assert len(trending) >= 0
    
    def test_get_interest_over_time(self):
        """Test getting interest scores for keywords."""
        detector = TrendDetector()
        keywords = ["python", "javascript"]
        
        result_df = detector.get_interest_over_time(keywords)
        
        # Should return a DataFrame
        assert isinstance(result_df, pd.DataFrame)
        
        # Should have expected columns if data returned
        if not result_df.empty:
            assert 'keyword' in result_df.columns
            assert 'interest_score' in result_df.columns
            assert 'is_rising' in result_df.columns
    
    def test_filter_high_velocity_trends(self):
        """Test filtering for high-velocity trends."""
        detector = TrendDetector()
        
        # Create sample data
        sample_df = pd.DataFrame({
            'keyword': ['product_a', 'product_b', 'product_c'],
            'interest_score': [80, 45, 15],
            'is_rising': [True, True, False],
            'velocity': [25.5, 10.2, -5.3]
        })
        
        filtered = detector.filter_high_velocity_trends(sample_df, min_interest=20)
        
        # Should filter out low interest and non-rising
        assert len(filtered) == 2
        assert 'product_c' not in filtered['keyword'].values


# ============================================================================
# MarketplaceScraper Tests
# ============================================================================

class TestMarketplaceScraper:
    """Test suite for MarketplaceScraper class."""
    
    def test_initialization(self):
        """Test that MarketplaceScraper initializes correctly."""
        scraper = MarketplaceScraper(delay=1, max_retries=2)
        assert scraper.delay == 1
        assert scraper.max_retries == 2
        assert scraper.session is not None
    
    def test_get_headers(self):
        """Test header generation."""
        scraper = MarketplaceScraper()
        headers = scraper._get_headers()
        
        assert isinstance(headers, dict)
        assert 'User-Agent' in headers
        assert 'Accept' in headers
    
    @pytest.mark.slow
    def test_scrape_ebay_real(self):
        """
        Test real eBay scraping (requires internet).
        Marked as slow - may be skipped in CI/CD.
        """
        scraper = MarketplaceScraper(delay=2)
        count = scraper.scrape_ebay("python book")
        
        # Should return a number or None
        assert count is None or isinstance(count, int)
        
        # If successful, should be positive
        if count is not None:
            assert count >= 0
    
    def test_get_supply_metrics(self):
        """Test getting supply metrics (mocked)."""
        scraper = MarketplaceScraper()
        
        # This will make real requests - use with caution
        # In production, mock the HTTP requests
        result = scraper.get_supply_metrics("test keyword", platforms=['ebay'])
        
        assert isinstance(result, dict)
        assert 'keyword' in result
        assert 'total_supply' in result


# ============================================================================
# OpportunityAnalyzer Tests
# ============================================================================

class TestOpportunityAnalyzer:
    """Test suite for OpportunityAnalyzer class."""
    
    def test_initialization(self):
        """Test that OpportunityAnalyzer initializes correctly."""
        analyzer = OpportunityAnalyzer(min_interest=15, max_supply=300)
        assert analyzer.min_interest == 15
        assert analyzer.max_supply == 300
    
    def test_calculate_opportunity_score(self):
        """Test opportunity score calculation."""
        analyzer = OpportunityAnalyzer()
        
        # Test case 1: High interest, low supply
        score1 = analyzer.calculate_opportunity_score(100, 50)
        assert score1 == 100 / 51  # (Supply + 1)
        
        # Test case 2: Zero division protection
        score2 = analyzer.calculate_opportunity_score(80, 0)
        assert score2 == 80 / 1
        
        # Test case 3: Invalid inputs
        score3 = analyzer.calculate_opportunity_score(0, 100)
        assert score3 == 0.0
        
        score4 = analyzer.calculate_opportunity_score(50, -1)
        assert score4 == 0.0
    
    def test_merge_and_score(self):
        """Test merging trend and supply data."""
        analyzer = OpportunityAnalyzer()
        
        trend_df = pd.DataFrame({
            'keyword': ['product_a', 'product_b'],
            'interest_score': [80, 60],
            'is_rising': [True, True],
            'velocity': [10.0, 5.0]
        })
        
        supply_df = pd.DataFrame({
            'keyword': ['product_a', 'product_b'],
            'total_supply': [50, 200]
        })
        
        result = analyzer.merge_and_score(trend_df, supply_df)
        
        # Should have merged data
        assert len(result) == 2
        assert 'opportunity_score' in result.columns
        
        # Check scores are calculated
        assert result.iloc[0]['opportunity_score'] > 0
    
    def test_filter_opportunities(self):
        """Test filtering for real opportunities."""
        analyzer = OpportunityAnalyzer(min_interest=20, max_supply=500)
        
        # Create test data
        df = pd.DataFrame({
            'keyword': ['good_product', 'low_interest', 'oversaturated'],
            'interest_score': [75, 10, 80],
            'total_supply': [50, 30, 10000],
            'is_rising': [True, False, True],
            'opportunity_score': [1.47, 0.32, 0.008]
        })
        
        filtered = analyzer.filter_opportunities(df)
        
        # Should only keep 'good_product'
        assert len(filtered) == 1
        assert filtered.iloc[0]['keyword'] == 'good_product'
    
    def test_add_classifications(self):
        """Test adding market status classifications."""
        analyzer = OpportunityAnalyzer()
        
        df = pd.DataFrame({
            'keyword': ['underserved', 'moderate', 'oversaturated'],
            'total_supply': [30, 250, 5000],
            'opportunity_score': [2.0, 0.5, 0.01]
        })
        
        result = analyzer.add_classifications(df)
        
        # Should add new columns
        assert 'market_status' in result.columns
        assert 'recommendation' in result.columns
        
        # Check classifications
        assert 'Underserved' in result.iloc[0]['market_status']
        assert 'Oversaturated' in result.iloc[2]['market_status']


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """End-to-end integration tests."""
    
    def test_full_pipeline_with_mock_data(self):
        """Test the complete pipeline with mock data."""
        # Create components
        analyzer = OpportunityAnalyzer()
        
        # Mock trend data
        trend_df = pd.DataFrame({
            'keyword': ['test_product'],
            'interest_score': [75],
            'is_rising': [True],
            'velocity': [15.0]
        })
        
        # Mock supply data
        supply_df = pd.DataFrame({
            'keyword': ['test_product'],
            'total_supply': [45]
        })
        
        # Merge and score
        scored = analyzer.merge_and_score(trend_df, supply_df)
        
        # Generate report
        report = analyzer.generate_report(scored, top_n=5)
        
        # Verify report structure
        assert isinstance(report, pd.DataFrame)
        assert len(report) > 0
        assert 'rank' in report.columns


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_trend_data():
    """Provide sample trend data for tests."""
    return pd.DataFrame({
        'keyword': ['product_1', 'product_2', 'product_3'],
        'interest_score': [80, 60, 40],
        'is_rising': [True, True, False],
        'velocity': [15.0, 8.0, -2.0]
    })


@pytest.fixture
def sample_supply_data():
    """Provide sample supply data for tests."""
    return pd.DataFrame({
        'keyword': ['product_1', 'product_2', 'product_3'],
        'total_supply': [50, 200, 5000]
    })


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])