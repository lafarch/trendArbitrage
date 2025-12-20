# TrendArbitrage

**Automated dropshipping niche discovery engine.** Identifies profitable products by analyzing demand trends and marketplace supply saturation.

---
## Quick Setup

1. **Install dependencies**:
```bash
   pip install -r requirements.txt
```

2. **Get SerpAPI Key**: Sign up at [serpapi.com](https://serpapi.com)

3. **Configure**:
```bash
   # Create .env file
   echo "SERPAPI_KEY=your_key_here" > .env
```

4. **Run**:
```bash
   # Web interface
   streamlit run app.py
   
   # CLI
   python main.py --keywords "your keywords"
```
## Web Dashboard

Interactive interface for real-time analysis:
```bash
streamlit run app.py
```

**Features**:
- Multi-keyword analysis
- Real-time supply scanning (Amazon, eBay, Walmart, AliExpress)
- Interactive scatter plots (Demand vs Supply)
- Historical trend simulation
- Downloadable reports

**Usage**:
1. Enter keywords (comma-separated)
2. Select marketplaces to scan
3. Click "ANALYZE MARKET"
4. View opportunity scores + verdicts

---

## How It Works

### Pipeline Overview

```
1. Trend Detection (Google Trends + Shopping)
   ↓
2. Supply Scraping (Amazon, eBay via SerpAPI)
   ↓
3. Opportunity Scoring (0-100, demand/supply ratio)
   ↓
4. Report Generation (CSV + detailed verdicts)
```

---
## Core Metrics Explained

### 1. **Opportunity Score (0-100)**

Simplified viability metric: qualified demand vs logarithmic competition, amplified by momentum.

**Formula:**
```
Demand Signal = monthly_searches × (purchase_intent / 100)
Supply Pressure = log₁₀(total_supply + 10)
Base Ratio = Demand Signal / Supply Pressure

Momentum Multiplier = 1 + (velocity × 0.5)  # Range: 1x to 2x

Final Score = (Base Ratio × Momentum Multiplier) / 50
Final Score = clamp(0, 100) - saturation_penalty
```

**Why this works:**
- **Demand Signal**: Raw searches adjusted by buying intent (informational searches ≠ buyers)
- **Supply Pressure**: Logarithmic (10k vs 20k competitors has minimal marginal impact)
- **Momentum is MULTIPLICATIVE**: Growth amplifies opportunity, doesn't just add to it
- **No revenue theater**: No fictional conversion rates or price projections

**Score Ranges:**
- **70-100**: Excellent. High qualified demand, low competition.
- **50-69**: Viable. Good ratio, requires strong execution.
- **30-49**: Risky. Compressed margins or weak demand.
- **0-29**: Avoid. Fundamentals don't work.

**Example (Yoga Mat):**
```
Monthly searches: 7,200
Purchase intent: 60/100
→ Demand Signal: 7,200 × 0.6 = 4,320

Total supply: 29,579 listings
→ Supply Pressure: log₁₀(29,579) = 4.47

Base Ratio: 4,320 / 4.47 = 967

Velocity: 0.09
→ Momentum: 1 + (0.09 × 0.5) = 1.045x

Score: (967 × 1.045) / 50 = 20.2
- Saturation Penalty: -10 (>10k listings)
= Final Score: 10.2/100 ❌
```

---

### 2. **Monthly Searches**

Estimated real search volume derived from Google Trends relative interest.

**Scaling Method:**
```python
# Google Trends returns 0-100 relative interest
# We scale to absolute monthly searches:
monthly_searches = (interest_score / 100) × 10,000

# Examples:
# Interest 100 → 10,000 searches/month
# Interest 50  → 5,000 searches/month
# Interest 10  → 1,000 searches/month
```

**Limitation:** This is an estimate. Actual volumes may vary, but ratios between keywords remain proportional.

**Source:** SerpAPI Google Trends (12-month historical data)

---

### 3. **Purchase Intent Score (0-100)**

Measures commercial intent based on Google Shopping activity.

**Components:**
- **Shopping Results Available (0-40 pts):** Products actively listed
- **Product Presence (0-30 pts):** Results in first page (market activity)
- **Product Variety (0-30 pts):** Multiple sellers (competitive market)

**Interpretation:**
- **70-100**: Transactional keywords (people ready to buy)
- **40-70**: Mixed intent (research + buying)
- **0-40**: Informational (low purchase likelihood)

**Why no prices?**
Price extraction is unreliable and doesn't improve scoring accuracy. Purchase intent from product availability is sufficient.

**Source:** SerpAPI Google Shopping API

---

### 4. **Demand Signal**

Qualified monthly searches adjusted for buying intent.

```
Demand Signal = monthly_searches × (purchase_intent / 100)

Example:
10,000 searches × 0.7 intent = 7,000 qualified searches
10,000 searches × 0.3 intent = 3,000 qualified searches
```

This separates "bluetooth headphones" (high intent) from "bluetooth headphones history" (informational).

---

### 5. **Competition Level**

Supply saturation classification based on total marketplace listings.

**Levels:**
- **BLUE OCEAN 🌊** (<100 listings): Untapped market
- **LOW 🟢** (100-499): Minimal competition
- **MODERATE 🟡** (500-1,999): Healthy competition
- **HIGH 🟠** (2,000-9,999): Saturated market
- **EXTREME 🔴** (10,000+): Highly saturated

**Source:** SerpAPI Amazon + eBay product search results

---

### 6. **Supply Pressure**

Logarithmic competition metric reflecting diminishing competitive impact at scale.

```
Supply Pressure = log₁₀(total_supply + 10)

Examples:
100 listings    → log₁₀(110) = 2.04
1,000 listings  → log₁₀(1,010) = 3.00
10,000 listings → log₁₀(10,010) = 4.00
20,000 listings → log₁₀(20,010) = 4.30
```

**Why logarithmic?**
The competitive difference between 100 and 1,000 sellers is massive (you're buried on page 10). Between 10,000 and 20,000, you're equally invisible—the impact plateaus.

---

### 7. **Base Ratio (Demand/Supply)**

Core economics: qualified demand per unit of competition.

```
Base Ratio = Demand Signal / Supply Pressure

Interpretation:
> 5,000  → Excellent (abundant qualified demand per pressure unit)
2,000-5,000 → Good (viable market)
500-2,000 → Challenging (tight margins)
< 500 → Critical (avoid)
```

This is the fundamental metric before momentum amplification.

---

### 8. **Trend Velocity**

Growth momentum calculated as slope of interest over time.

```
velocity = trend_slope(interest_values_over_12_months)

Interpretation:
velocity > 1.0  → Rapid growth (viral potential)
velocity > 0.5  → Steady growth
velocity > 0    → Slow growth
velocity ≤ 0    → Declining interest
```

**Why velocity matters:**
A keyword with velocity 1.5 is experiencing exponential growth—demand next month will be higher than this month.

---

### 9. **Momentum Multiplier**

Amplification factor applied to base ratio.

```
Momentum Multiplier = 1 + (velocity × 0.5)
Capped at 2.0x maximum

Examples:
velocity 0.0  → 1.00x (no amplification)
velocity 0.5  → 1.25x
velocity 1.0  → 1.50x
velocity 2.0  → 2.00x (viral, doubles the score)
```

**Why multiplicative?**
Growth amplifies opportunity—it doesn't just add a bonus. A product with 5,000 demand and 2x momentum is fundamentally different from 5,000 demand + flat growth.

---

### 10. **Saturation Penalty**

Additional penalty for extreme competition.

```
total_supply > 20,000  → -15 pts
total_supply > 10,000  → -10 pts
Otherwise              → 0 pts
```

Prevents scores from looking viable when competition is insurmountable.

---

## Output Interpretation

### Summary Table

```
┏━━━━━━┳━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Rank ┃ Keyword   ┃  Score ┃   Demand   ┃   Supply   ┃ Competition  ┃ Status     ┃
┃  1   ┃ yoga mat  ┃  10.2  ┃    4,320   ┃   29,579   ┃ EXTREME 🔴   ┃ ❌ EVITAR  ┃
```

**Key insights:**
- **Score 10.2/100:** Economically unviable
- **Demand Signal 4,320:** Decent qualified demand exists
- **29,579 listings:** Market is oversaturated (pressure 4.47)
- **Base Ratio 967:** Demand/pressure insufficient to overcome saturation

---

### Detailed Verdict

The verdict explains mathematically why a product scores high or low.

**For Low Scores (0-29):**
```
❌ EVITAR (10.2/100)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Demanda cualificada: 4,320 búsquedas/mes
Competencia: 29,579 ofertas (EXTREME 🔴)
Ratio D/S: 967.2 (CRÍTICO)

💀 Problema crítico: Extrema saturación (29,579 ofertas)
   Supply pressure 4.47 divide tu demanda hasta volverla inviable
   Momentum: 1.05x (no salva el ratio base)

→ Mercado inviable. Buscar otro nicho.
```

**Key diagnosis:**
- Problem identified: Extreme saturation crushes the ratio
- Mathematical explanation: Even with momentum amplification, base ratio is too low
- Verdict: Avoid—unit economics don't work

---

## Temporal Analysis

Running with `--temporal` flag generates multi-timeframe analysis (7d, 1m, 3m, 6m, 12m).

**Purpose:**
- Validate consistency: Is growth sustainable or a temporary spike?
- Identify emerging trends: Did velocity increase recently?
- Risk assessment: Longer timeframes reduce noise

**Output:** `data/output/temporal_analysis.csv`

```csv
keyword,period,score,demand_signal,competition_level,trend_velocity,momentum_multiplier,data_points
yoga mat,7d,15.2,5100,EXTREME 🔴,0.85,1.43,7
yoga mat,1m,12.8,4680,EXTREME 🔴,0.42,1.21,30
yoga mat,3m,10.2,4320,EXTREME 🔴,0.09,1.05,90
```

**Interpretation:**
- **7d score (15.2)**: Recent spike with high velocity (0.85)
- **1m score (12.8)**: Velocity normalizing (0.42)
- **3m score (10.2)**: Long-term average shows weak fundamentals (0.09)

**Verdict:** The 7-day spike is noise. 3-month view reveals the true (poor) opportunity.

---

## Usage

```bash
# Basic analysis
python main.py --keywords "phone case,yoga mat"

# Use trending searches
python main.py --trending

# Generate temporal analysis (recommended)
python main.py --keywords "bluetooth headphones" --temporal
```

---

## Data Sources

| Metric | Source | API |
|--------|--------|-----|
| Interest trends | Google Trends | SerpAPI |
| Purchase intent | Google Shopping | SerpAPI |
| Supply counts | Amazon, eBay | SerpAPI |

All scraping handled by SerpAPI to avoid bot detection.

---

## Limitations

1. **Estimated search volumes:** Relative interest scaled to 10k baseline (not absolute Google data)
2. **Purchase intent heuristic:** Based on product availability, not actual click-through data
3. **Competition counts:** Total listings (doesn't assess seller quality/ranking)
4. **No cost data:** Doesn't factor in CAC, COGS, or margin estimates

**Recommendation:** Use scores as initial screening. Validate top opportunities (score >50) with manual research before investing capital.

---

## Key Takeaways

- **Opportunity Score = (Demand/Competition) × Momentum** in a single 0-100 metric
- **Momentum is multiplicative** because growth amplifies opportunity, not adds to it
- **No revenue projections** because they're unreliable without real conversion/pricing data
- **Temporal analysis is critical** to separate noise from signal
- **Score >70 = strong fundamentals, not guaranteed profit**

Use this tool to filter noise and focus research on mathematically sound niches.