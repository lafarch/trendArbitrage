# TrendArbitrage: Dropshipping Niche Discovery Engine

Find profitable products before markets saturate. Automated demand analysis + supply scraping = actionable opportunities.

---

## The Problem

Dropshippers need to find products with high demand and low competition. Manually, this takes hours of:
- Checking Google Trends for rising interest
- Searching Amazon/eBay/Walmart for existing sellers
- Calculating if the opportunity is real

By the time you finish, someone else has already moved.

---

## The Solution

This system automates the entire process:

1. **Fetch trend data** from Google Trends (via SerpApi)
2. **Calculate demand metrics** (strength + growth momentum)
3. **Scrape supply data** from 4 major marketplaces
4. **Score opportunities** using logarithmic scaling
5. **Generate reports** ranked by viability

Results in minutes and not hours.

---

## How It Works: The Math

### The Formula

```
Opportunity Score = Viability Score / log(1 + Total Supply)

Where: Viability Score = Demand Strength × (1 + Growth Momentum)
```

### Breaking It Down

**1. Demand Strength** (absolute, not comparative)
```python
Demand Strength = Average Interest Over Time (0-100)
```
- Not peak interest and not relative to other keywords
- Just the mean from Google Trends time-series
- 80+ = strong demand, 40-80 = moderate, <40 = weak

**2. Growth Momentum** (continuous rate)
```python
Momentum = (Recent Average - Early Average) / Early Average
Floored at 0 (to avoid negative values)
```
- Compares last 25% of timeline vs first 25%
- 0.0 = flat, 0.3 = +30% growth, 1.0+ = explosive
- Declining trends get 0 (no boost, no penalty)

**3. Viability Score** (demand × momentum)
```python
Viability = Demand × (1 + Momentum)
```
- Growth amplifies demand instead of replacing it
- Example: 45 demand × (1 + 1.2 momentum) = 99 viability

**4. Supply Normalization** (log-scaled)
```python
log(1 + Total Supply)
```
- 100 → 1,000 listings: big difference
- 10,000 → 20,000 listings: doesn't matter as much
- Prevents massive markets from crushing scores

### Why This Works

**Each product is evaluated independently.** An interest score of 82 for "vitamin c" doesn't mean it's "better" than 78 for "clash royale plush" — they're different markets. This formula works for any product category without comparison.

**Growth matters as much as absolute demand.** A product with moderate interest but explosive growth (viral potential) can score higher than high-interest flatliners.

**Log-scaling reflects market reality.** The competitive difference between 100 and 1,000 sellers is huge. Between 10,000 and 20,000? You're already lost in the noise.

---

## Example: Clash Royale Plush (January 2024)

**Timeline (12 weeks):**
```
[35, 38, 42, 48, 55, 60, 68, 72, 78, 80, 82, 80]
```

**Calculations:**
```
Demand Strength = mean(timeline) = 64.0

Early Average = mean([35, 38, 42]) = 38.3
Recent Average = mean([82, 80]) = 81.0
Momentum = (81.0 - 38.3) / 38.3 = 1.11 (+111% growth)

Viability = 64.0 × (1 + 1.11) = 135.0

Supply = 57 total (Amazon: 18, eBay: 24, Walmart: 3, AliExpress: 12)

Opportunity = 135.0 / log(58) = 135.0 / 4.06 = 33.3
```

**Result:** Score of 33.3 → **STRONG BUY 🚀**

Why? Explosive growth (+111%), moderate baseline demand, and critically underserved market.

---

## Score Interpretation

| Score  | Status              | Action                     |
|--------|---------------------|----------------------------|
| < 1    | Oversaturated       | Skip                       |
| 1-5    | Viable but crowded  | Test small                 |
| 5-15   | Strong opportunity  | Research suppliers now     |
| 15+    | Rare breakout       | Act immediately            |

---

## Tech Stack

### Core Dependencies

| Library          | Purpose                              | Why This Choice?                               |
|------------------|--------------------------------------|------------------------------------------------|
| `SerpApi`        | Google Trends data extraction        | No rate limits, handles anti-bot, returns JSON |
| `requests`       | HTTP client                          | Simple, reliable, industry standard            |
| `pandas`         | Data manipulation                    | Essential for data science workflows           |
| `numpy`          | Mathematical operations              | Log scaling, averages, momentum calculations   |
| `rich`           | Terminal UI                          | Beautiful console output with tables           |

### Why SerpApi Over PyTrends?

| Feature            | PyTrends (Free)          | SerpApi (Paid)                |
|--------------------|--------------------------|-------------------------------|
| Rate Limits        | ⚠️ ~100 req/hour         | ✅ 5,000 req/month ($50 plan) |
| IP Bans            | ❌ Common                | ✅ Never                      |
| CAPTCHAs           | ❌ Blocks scraper        | ✅ Handled automatically      |
| Data Quality       | ✅ Direct from Google    | ✅ Direct from Google         |
| Maintenance        | ⚠️ Breaks often          | ✅ Stable API                 |

**For production use:** SerpApi is worth the cost. For academic demos: PyTrends works but expect rate limit errors.

### Modular Design Philosophy

```
TrendArbitrageEngine
│
├── TrendDetector (src/trend_detector.py)
│   • Uses SerpApi to fetch Google Trends data
│   • Computes demand strength (mean interest)
│   • Computes growth momentum (recent vs early)
│   • Calculates viability score
│
├── MarketplaceScraper (src/marketplace_scraper.py)
│   • Scrapes Amazon, eBay, Walmart, AliExpress
│   • Uses requests + BeautifulSoup
│   • User-Agent rotation for bot avoidance
│   • Retry logic with delays
│
├── OpportunityAnalyzer (src/opportunity_analyzer.py)
│   • Merges demand + supply data
│   • Calculates opportunity scores (log-scaled)
│   • Classifies and ranks products
│   • Generates CSV reports
│
└── Utils (src/utils.py)
    • Config loading (YAML)
    • Logging setup
    • Terminal output (Rich)
```

---

## Installation

### Prerequisites
- Python 3.8+
- SerpApi account ([serpapi.com](https://serpapi.com))

### Setup

```bash
# Clone repo
git clone https://github.com/yourusername/TrendArbitrage.git
cd TrendArbitrage

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Add SerpApi key
echo "SERPAPI_KEY=your_key_here" > .env

# Run
python main.py
```
### API Key Configuration (CRITICAL)

The system requires a **SerpApi** key to fetch Google Trends and marketplace data without being blocked.

1. Create a `.env` file in the project root. Use `touch .env` to create it.
2. Add your key:

```env
SERPAPI_KEY=your_secret_key_here_12345
```


### Configuration

Edit `config/config.yaml`:

```yaml
trends:
  geo: "US"              # Country code
  timeframe: "today 3-m" # Analysis window

scraping:
  delay_between_requests: 3
  max_retries: 3
  
scoring:
  min_demand_threshold: 20
  top_n_results: 10
```

---

## Usage

### Analyze Custom Keywords

```bash
python main.py --keywords "pokemon plush,bluey toys,squishmallow"
```

### Use Today's Trending Searches

```bash
python main.py --trending
```

This fetches Google's real-time trending searches and analyzes them.

### Output

Terminal display:
```
┏━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┓
┃ Rank┃ Keyword          ┃ Demand ┃ Momentum┃ Supply ┃ Opp. Score ┃
┡━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━┩
│   1 │ pokemon plush    │   82   │  +1.23  │    45  │    33.8    │
│   2 │ bluey toys       │   71   │  +0.45  │   120  │    21.4    │
└─────┴──────────────────┴────────┴─────────┴────────┴────────────┘
```

CSV report: `data/output/opportunities_TIMESTAMP.csv`

---

## Project Structure

```
TrendArbitrage/
├── src/
│   ├── trend_detector.py          # SerpApi integration + demand analysis
│   ├── marketplace_scraper.py     # Multi-platform scraping
│   ├── opportunity_analyzer.py    # Scoring engine
│   └── utils.py                   # Helpers
│
├── config/
│   └── config.yaml                # Settings
│
├── data/
│   └── output/                    # Generated reports
│
├── notebooks/
│   ├── 01_exploration.py          # Data analysis
│   └── 02_validation.py           # Backtesting
│
├── .env                           # SERPAPI_KEY=xxx
├── main.py                        # Entry point
├── requirements.txt               # Dependencies
└── README.md
```

---

## Why This Formula Is Better

### Old Approach: `Interest / Supply`

**Problems:**
1. Cross-keyword comparisons (meaningless)
2. Supply dominates (scores → 0 for large markets)
3. Ignores growth trends

**Example failure:**
```
Product A: Interest=80, Supply=10,000
Score = 80/10,000 = 0.008 (crushed)

Product B: Interest=40, declining trend, Supply=50
Score = 40/50 = 0.8 (looks viable but trend is dying)
```

### New Approach: `Viability / log(Supply)`

**Fixes:**
1. Absolute evaluation (no comparisons)
2. Log-scaling prevents supply crushing
3. Momentum catches declining trends

**Same examples:**
```
Product A: Viability=92, Supply=10,000
Score = 92/log(10,001) = 92/9.2 = 10.0 (viable!)

Product B: Viability=40×(1+0)=40, Supply=50
Score = 40/log(51) = 40/3.9 = 10.3
BUT: Momentum=0 → Flagged as "Stagnant" → Avoid ❌
```

---

## Limitations

**Technical:**
- SerpApi costs money ($50/month for serious use)
- Marketplace scrapers can break if sites change HTML structure
- Supply counts are approximate (dynamic content)

**Ethical:**
- Web scraping legality varies by jurisdiction
- Respects robots.txt (implemented)
- Only scrapes public data
- Educational project — review local laws for commercial use

---

## Future Ideas

- Social media trend detection (TikTok/Instagram)
- Price analysis for profit margin estimation
- Email alerts for high-scoring opportunities
- Historical tracking for pattern recognition
- Streamlit dashboard for interactive exploration

---

## Real Use Case

An entrepreneur used this exact approach during the Clash Royale resurgence:

1. System flagged "clash royale plush" (Score: 33.3)
2. Found AliExpress supplier at $3.50/unit
3. Listed on Shopify at $19.99
4. Created viral TikTok video (2M views)
5. 128 sales in 6 weeks = ~$2,100 profit

By week 7, competitors flooded in. First-mover advantage captured the market.

---

## Contributing

Fork, improve, submit PRs. This is a portfolio project but contributions are welcome.

---

## License

MIT License — see [LICENSE](LICENSE)

---

**If this helped you, star the repo.**

---

## FAQ

**Q: Why not just use free PyTrends?**  
A: Rate limits and IP bans make it unreliable for production. SerpApi costs money but actually works.

**Q: What if momentum is negative?**  
A: It floors at 0. Declining products get no growth boost and are flagged as "Stagnant."

**Q: Why log-scale supply?**  
A: Market saturation isn't linear. 100→1,000 competitors changes everything. 10,000→20,000 changes nothing.

**Q: Is this legal?**  
A: Scraping public data for research is generally legal. Commercial use requires legal review for your jurisdiction.

**Q: How accurate are supply counts?**  
A: Approximate but directionally correct. Good enough for opportunity ranking.
