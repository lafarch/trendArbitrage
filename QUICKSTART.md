# 🚀 TrendArbitrage - Quick Start Guide

Get up and running in 5 minutes!

---

## Step 1: Clone & Setup (2 minutes)

```bash
# Clone the repository
git clone https://github.com/yourusername/TrendArbitrage.git
cd TrendArbitrage

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 2: Run Your First Analysis (1 minute)

```bash
# Basic run with default keywords
python main.py
```

**Expected output:**
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

#1 🚀 STRONG BUY
   Keyword: clash royale plush
   📊 Interest Score: 75/100
   📦 Supply Count: 45 products
   ⚡ Opportunity Score: 1.6304
   🏪 Market Status: Underserved ⭐⭐⭐
```

---

## Step 3: Analyze Custom Keywords (30 seconds)

```bash
# Analyze your own product ideas
python main.py --keywords "pokemon plush,zelda merchandise,anime figures"
```

---

## Step 4: Use Real-Time Trending Searches (1 minute)

```bash
# Fetch TODAY's trending searches automatically
python main.py --trending
```

This will automatically fetch what people are searching for RIGHT NOW and analyze those products.

---

## Step 5: Check Your Results

Your CSV report is saved in `data/output/opportunities_TIMESTAMP.csv`

Open it in Excel/Google Sheets to see:
- **Rank:** 1-N based on opportunity score
- **Keyword:** Product name
- **Interest Score:** Google search popularity (0-100)
- **Supply Count:** Number of existing products
- **Opportunity Score:** Our calculated "profit potential"
- **Market Status:** Underserved / Low Competition / Oversaturated
- **Recommendation:** STRONG BUY / Consider / Risky / Avoid

---

## Common Use Cases

### 1. Daily Opportunity Scanner
Run every morning to catch new trends:
```bash
python main.py --trending > daily_report.txt
```

### 2. Validate Your Product Ideas
Have product ideas? Test them:
```bash
python main.py --keywords "your product 1,your product 2,your product 3"
```

### 3. Niche Research for TikTok Shop
Find products perfect for short-form video:
```bash
python main.py --keywords "viral toy,trending gadget,tiktok must have"
```

---

## Troubleshooting

### Issue: "No module named 'pytrends'"
**Solution:** Make sure you activated the virtual environment and ran `pip install -r requirements.txt`

### Issue: "Rate limit exceeded"
**Solution:** The scraper is being respectful with delays. If you hit rate limits:
1. Increase delay in `config/config.yaml`: `delay_between_requests: 5`
2. Run with fewer keywords at a time

### Issue: "eBay returned 0 results for everything"
**Solution:** 
- Check your internet connection
- eBay may have changed their HTML structure (update the scraper)
- Try running again in a few minutes (temporary block)

### Issue: "CAPTCHA detected"
**Solution:** Set `use_selenium: true` in `config/config.yaml` (slower but more reliable)

---

## Next Steps

✅ **Check the full README.md** for detailed documentation  
✅ **Open `notebooks/01_exploration.ipynb`** to visualize your data  
✅ **Customize `config/config.yaml`** for your preferences  
✅ **Read the code comments** to understand how it works  

---

## Need Help?

- **Documentation:** See [README.md](README.md)
- **Issues:** Open a GitHub issue
- **Questions:** Check the comments in the source code

---

**Happy arbitrage hunting! 🎯💰**