# 🚀 TrendArbitrage - Quick Start Guide

Get up and running in 5 minutes!

---

## Step 1: Clone & Setup (2 minutes)

```bash
# Clone the repository
git clone [https://github.com/yourusername/TrendArbitrage.git](https://github.com/yourusername/TrendArbitrage.git)
cd TrendArbitrage

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies (Core + Frontend)
pip install -r requirements.txt
pip install streamlit plotly 
```

---

## Step 2: Launch Web Dashboard (Recommended)
The easiest way to analyze markets is using the new interactive interface.

```bash
# Basic run with default keywords
streamlit run app.py
```

This will automatically open your browser at http://localhost:8501.

How to use:

    Enter Keywords: Type products separated by commas (e.g., yoga mat, mechanical keyboard).

    Select Sources: Choose which marketplaces to scan (Amazon, eBay, Walmart, AliExpress).

    Analyze: Click "ANALYZE MARKET" to see real-time opportunities.



## Step 3: CLI Usage (Advanced / Automation)

If you prefer the terminal or want to run automated cron jobs:

```bash
# Analyze specific keywords
python main.py --keywords "pokemon plush,zelda merchandise"

```
**Expected functionality example:**
```
🎯 TrendArbitrage v1.0
AI-Powered Dropshipping Niche Discovery Engine

🚀 STARTING TRENDARBITRAGE PIPELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Analyzing 10 keywords:
   1. clash royale plush
   2. skibidi toilet toy
   ...

📈 Phase 2: Analyzing search interest...
✅ Retrieved interest data for 10 keywords

🛒 Phase 3: Checking marketplace supply...
   Scraping: clash royale plush...
✅ Retrieved supply data for 10 keywords

🎯 Phase 4: Calculating Opportunity Scores...
✅ Calculated scores for 10 products

📊 Phase 5: Generating opportunity report...
✅ Report saved: data/output/opportunities_20240115_143022.csv

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 TOP 3 DROPSHIPPING OPPORTUNITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋

# ❌ EVITAR (9.6/100) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Demanda cualificada: 1,616 búsquedas/mes 🔴 Competencia: 2,226 ofertas 🔴 Ratio D/S: 482.50 (CRÍTICO)

   💀 Problema crítico: Ratio D/S crítico (482.50) Demanda 1,616 ÷ Pressure 3.35 = ratio pésimo Momentum: 1.00x (no salva el ratio base)

   → Mercado inviable. Buscar otro nicho.
```



---

---

## Step 4: Check Your Results

If using the Dashboard:

    Visuals: Real-time scatter plots (Demand vs Supply) and Sales Simulations.

    Data: Detailed JSONs are saved to data/frontend/.

If using the CLI:

    Report: Your CSV is saved in data/output/report.csv.

    Columns: Rank, Keyword, Opportunity Score, Demand Signal, Total Supply, Verdict.

Troubleshooting
Issue: "Streamlit is not recognized"

Solution: Make sure you activated the virtual environment and ran pip install streamlit plotly.
Issue: "Rate limit exceeded"

Solution: The scraper is being respectful with delays. If you hit rate limits:

    Increase delay in config/config.yaml: delay_between_requests: 5

    Run with fewer keywords at a time.

Issue: "eBay/Walmart returned 0 results"

Solution:

    Check your internet connection.

    Ensure your SerpAPI key has remaining credits.

    Try running again in a few minutes (temporary IP block).

Next Steps

✅ Check the full README.md for detailed documentation on metrics.

✅ Customize config/config.yaml to adjust thresholds.

✅ Read the code comments to understand the "Opportunity Score" math.

Happy arbitrage hunting!