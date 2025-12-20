# 🚀 TrendArbitrage - Quick Start

Get running in **3 minutes**.

---

## Step 1: Install (1 min)
```bash
git clone https://github.com/yourusername/TrendArbitrage.git
cd TrendArbitrage

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

---

## Step 2: Configure API Key (1 min)

**Get SerpAPI Key** (required for data):
1. Sign up at https://serpapi.com (100 free searches/month)
2. Copy your API key

**Create `.env` file** in project root:
```bash
SERPAPI_KEY=your_key_here
```

---

## Step 3: Run (1 min)

### Option A: Web Dashboard (Recommended)
```bash
streamlit run app.py
```
Opens browser at `http://localhost:8501`

How to use:

    Enter Keywords: Type products separated by commas (e.g., yoga mat, mechanical keyboard).

    Select Sources: Choose which marketplaces to scan (Amazon, eBay, Walmart, AliExpress).

    Analyze: Click "ANALYZE MARKET" to see real-time opportunities.

### Option B: CLI Usage (Advanced / Automation)

If you prefer the terminal or want to run automated cron jobs:

```bash
# Analyze specific products
python main.py --keywords "yoga mat,phone case"

# Use today's trending searches
python main.py --trending

# Generate temporal analysis
python main.py --keywords "bluetooth headphones" --temporal
```

---

## Understanding Results

**Opportunity Score (0-100)**:
- **70-100** 🚀 Excellent - High demand, low competition
- **50-69** 💡 Viable - Good fundamentals, needs execution
- **30-49** ⚠️ Risky - Compressed margins
- **0-29** ❌ Avoid - Economics don't work

**Key Metrics**:
- `Demand Signal`: Monthly qualified searches (intent-adjusted)
- `Supply Pressure`: log₁₀(competition) - logarithmic scale
- `Base Ratio`: Demand/Supply economics
- `Momentum`: Growth amplifier (1x to 2x)

---

## Troubleshooting

**"SERPAPI_KEY not found"**
→ Create `.env` file with your key (see Step 2)

**"Rate limit exceeded"**
→ SerpAPI free tier = 100 searches/month. Upgrade or wait.

**"No data returned"**
→ Check keyword spelling. Try broader terms first.

---

## Next Steps

📖 Read `README.md` for metric formulas  
⚙️ Customize `config/config.yaml` for thresholds  
📊 Export reports from `data/output/`

Happy arbitrage hunting!