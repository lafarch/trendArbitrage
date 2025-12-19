# TrendArbitrage

**Automated dropshipping niche discovery engine.** Identifies profitable products by analyzing demand trends and marketplace supply saturation.

---

## How It Works

### Pipeline Overview

```
1. Trend Detection (Google Trends + Shopping)
   ↓
2. Supply Scraping (Amazon, eBay via SerpAPI)
   ↓
3. Opportunity Scoring (0-100 economic viability)
   ↓
4. Report Generation (CSV + detailed verdicts)
```

---

## Core Metrics Explained

### 1. **Opportunity Score (0-100)**

Economic viability metric combining demand, competition, and momentum.

**Formula:**
```
Demand Monetized = monthly_searches × conversion_rate × avg_price
Supply Pressure = log₁₀(total_supply + 10)

Base Score (0-60) = Demand Monetized / Supply Pressure / 100
+ Purchase Intent Bonus (0-20)
+ Momentum Bonus (0-20)
- Saturation Penalty (0-30)
= Final Score (0-100)
```

**Score Ranges:**
- **80-100**: Gold mine. High demand, low competition. Act fast.
- **60-79**: Solid opportunity. Viable with good execution.
- **40-59**: Risky. Requires expertise and differentiation.
- **0-39**: Avoid. Poor demand/supply ratio.

**Example (Yoga Mat):**
```
Monthly searches: 7,200
Conversion rate: 2.5% (from purchase intent)
Avg price: $49.00
→ Demand Monetized: $8,842/month

Total supply: 29,579 listings
→ Supply Pressure: log₁₀(29,579) = 4.47

Base Score: 8,842 / 4.47 / 100 = 19.8
+ Intent Bonus: +12.0 (60/100 purchase intent)
+ Momentum: +5.0 (velocity: 0.09)
- Saturation Penalty: -30.0 (>10k listings)
= Final Score: 6.8/100 ❌
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

**Source:** SerpAPI Google Trends (12-month historical data)

---

### 3. **Purchase Intent Score (0-100)**

Measures commercial intent based on marketplace activity.

**Components:**
- **Shopping Results Available (0-40 pts):** Products listed on Google Shopping
- **Average Price Exists (0-30 pts):** Active market with pricing data
- **Product Variety (0-30 pts):** Multiple sellers indicate healthy competition

**Interpretation:**
- **70-100**: Transactional keywords (people ready to buy)
- **40-70**: Mixed intent (research + buying)
- **0-40**: Informational (low purchase likelihood)

**Source:** SerpAPI Google Shopping API

---

### 4. **Estimated Conversion Rate**

Predicted purchase rate based on purchase intent signals.

**Benchmarks:**
```
Purchase Intent 70-100  → 3.0% conversion (transactional)
Purchase Intent 50-70   → 2.5% conversion (medium intent)
Purchase Intent 30-50   → 1.5% conversion (research phase)
Purchase Intent 0-30    → 1.0% conversion (informational)
```

These rates reflect dropshipping industry standards (1-3%).

---

### 5. **Potential Monthly Revenue**

Theoretical revenue if capturing market share.

```
Revenue = monthly_searches × conversion_rate × avg_price

Example (Yoga Mat):
7,200 searches × 0.025 conversion × $49.00 = $8,842/month
```

This assumes you convert at the estimated rate. Actual revenue depends on:
- Product quality and differentiation
- Marketing effectiveness
- Pricing strategy
- Competition positioning

---

### 6. **Competition Level**

Supply saturation classification based on total marketplace listings.

**Levels:**
- **BLUE OCEAN 🌊** (<100 listings): Untapped market
- **LOW 🟢** (100-499): Minimal competition
- **MODERATE 🟡** (500-1,999): Healthy competition
- **HIGH 🟠** (2,000-9,999): Saturated market
- **EXTREME 🔴** (10,000+): Highly saturated

**Source:** SerpAPI Amazon + eBay product search results

---

### 7. **Supply Pressure**

Logarithmic competition metric reflecting diminishing competitive impact at scale.

```
Supply Pressure = log₁₀(total_supply + 10)

Examples:
100 listings   → log₁₀(110) = 2.04
1,000 listings → log₁₀(1,010) = 3.00
10,000 listings → log₁₀(10,010) = 4.00
```

**Why logarithmic?**
The competitive difference between 100 and 1,000 sellers is massive (you're buried on page 10). Between 10,000 and 20,000, you're equally invisible—the impact plateaus.

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

**Momentum Bonus:**
- **+20 pts**: velocity > 1.0 (explosive growth)
- **+10 pts**: velocity > 0.5 (healthy growth)
- **+5 pts**: velocity > 0 (slight growth)

---

### 9. **Demand/Supply Ratio**

Direct ratio showing monetized demand per competitor.

```
Ratio = potential_monthly_revenue / (total_supply + 1)

Example (Yoga Mat):
$8,842 / 29,580 = 0.299

Interpretation:
> 1.0   → Excellent (demand exceeds supply significantly)
0.5-1.0 → Good (balanced market)
0.1-0.5 → Poor (oversaturated)
< 0.1   → Critical (avoid)
```

---

### 10. **Score Breakdown**

Transparent decomposition of how the final score was calculated.

**Components:**
- **Base Score (0-60):** Core demand/supply economics
- **Intent Bonus (0-20):** Purchase readiness adjustment
- **Momentum Bonus (0-20):** Growth trend reward
- **Saturation Penalty (0-30):** Competition penalty

**Example (Yoga Mat):**
```
Base Score: 19.8/60 🔴  (weak fundamentals)
Intent Bonus: +12.0     (moderate buying intent)
Momentum: +5.0          (slight growth)
Saturation Penalty: -30.0 🔴 (extreme competition)
─────────────────────
Final Score: 6.8/100 ❌
```

---

## Output Interpretation

### Summary Table

```
┏━━━━━━┳━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Rank ┃ Keyword   ┃  Score ┃ Revenue/Mo ┃ Searches/Mo┃ Competition  ┃ Status     ┃
┃  1   ┃ yoga mat  ┃   6.8  ┃   $8,842   ┃    7,200   ┃ EXTREME 🔴   ┃ ❌ EVITAR  ┃
```

**Key insights:**
- **Score 6.8/100:** Economically unviable
- **Revenue $8,842/month:** Decent demand exists
- **29,579 listings:** Market is oversaturated (supply pressure 4.47)
- **Ratio 0.299:** Each competitor gets ~$0.30 revenue—unsustainable

---

### Detailed Verdict

The verdict explains mathematically why a product scores high or low.

**For Low Scores (0-39):**
```
❌ EVITAR (6.8/100)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Potencial mensual: $8,842
Competencia: 29,579 ofertas
Ratio D/O: 0.299 (PÉSIMO)

💀 Problema crítico: Extrema saturación (29,579 ofertas)
   Supply pressure = log₁₀(29,579) = 4.47
   → Divides tu revenue entre 4.47

→ Pérdida de tiempo y dinero garantizada.
```

**Key diagnosis:**
- Problem identified: Extreme saturation
- Mathematical explanation: High supply pressure (4.47) crushes the revenue potential
- Verdict: Avoid—poor unit economics

---

## Temporal Analysis

Running with `--temporal` flag generates multi-timeframe analysis (7d, 1m, 3m, 6m, 12m).

**Purpose:**
- Validate consistency: Is growth sustainable or a temporary spike?
- Identify emerging trends: Did velocity increase recently?
- Risk assessment: Longer timeframes reduce noise

**Output:** `data/output/temporal_analysis.csv`

```csv
keyword,period,score,potential_revenue,competition_level,trend_velocity,data_points
yoga mat,7d,8.2,8842,EXTREME 🔴,0.15,7
yoga mat,1m,7.5,8842,EXTREME 🔴,0.12,30
yoga mat,3m,6.8,8842,EXTREME 🔴,0.09,90
```

**Interpretation:** Score decreases with more data (velocity slows), confirming it's not an emerging opportunity.

---

## Usage

```bash
# Basic analysis
python main.py --keywords "phone case,yoga mat"

# Use trending searches
python main.py --trending

# Generate temporal analysis
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

1. **Estimated conversion rates:** Industry benchmarks, not product-specific
2. **Search volume scaling:** Relative interest scaled to 10k baseline (not absolute Google data)
3. **Price averages:** From top 20 Shopping results (may not reflect full market)
4. **Competition:** Counts all listings (doesn't assess quality/ranking)

**Recommendation:** Use scores as initial screening. Validate top opportunities with manual research before committing capital.

---

## Key Takeaways

- **Opportunity Score combines economics + momentum** into a single 0-100 metric
- **Log-scaled supply** reflects real competitive dynamics (10k vs 20k listings has minimal impact difference)
- **Verdicts explain WHY** a score is high/low using the underlying math
- **Temporal analysis** validates consistency and filters noise
- **Not a guarantee:** A score of 80 means strong fundamentals, not guaranteed profit

Use this tool to filter noise and focus manual research on high-potential niches.