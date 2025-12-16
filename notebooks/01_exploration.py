# %% [markdown]
# TrendArbitrage - Exploratory Data Analysis
# ============================================
# This notebook demonstrates data exploration and visualization
# for the TrendArbitrage project
# %%
# Cell 1: Setup
"""
Import necessary libraries for analysis and visualization
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Set visualization style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

print("✅ Libraries imported successfully")

# %%
# Cell 2: Load Sample Data
"""
Load the most recent opportunity report
"""
import glob
import os

# Find the most recent CSV in output folder
output_files = glob.glob("../data/output/opportunities_*.csv")
if output_files:
    latest_file = max(output_files, key=os.path.getctime)
    df = pd.read_csv(latest_file)
    print(f"✅ Loaded: {latest_file}")
    print(f"📊 Shape: {df.shape}")
    print(f"\n{df.head()}")
else:
    print("⚠️ No output files found. Run main.py first!")
    # Create sample data for demonstration
    df = pd.DataFrame({
        'rank': [1, 2, 3, 4, 5],
        'keyword': ['clash royale plush', 'skibidi toilet toy', 'digital circus plush', 
                    'poppy playtime toy', 'among us plush'],
        'interest_score': [75, 85, 65, 55, 40],
        'total_supply': [45, 120, 200, 380, 450],
        'opportunity_score': [1.63, 0.70, 0.32, 0.14, 0.09],
        'market_status': ['Underserved ⭐⭐⭐', 'Low Competition ⭐⭐', 
                         'Moderate Competition ⭐', 'Moderate Competition ⭐', 
                         'Moderate Competition ⭐'],
        'recommendation': ['STRONG BUY 🚀', 'Consider 💡', 'Risky ⚠️', 
                          'Risky ⚠️', 'Avoid ❌']
    })
    print("✅ Created sample data for demonstration")

# %%
# Cell 3: Data Overview
"""
Get statistical summary of the data
"""
print("="*60)
print("DATASET STATISTICS")
print("="*60)
print(df.describe())
print("\n")
print("="*60)
print("DATA TYPES")
print("="*60)
print(df.dtypes)

# %%
# Cell 4: Distribution of Interest Scores
"""
Visualize the distribution of search interest across products
"""
plt.figure(figsize=(12, 5))

# Histogram
plt.subplot(1, 2, 1)
plt.hist(df['interest_score'], bins=20, color='#3498db', edgecolor='black', alpha=0.7)
plt.xlabel('Interest Score (0-100)', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.title('Distribution of Search Interest', fontsize=14, fontweight='bold')
plt.axvline(df['interest_score'].mean(), color='red', linestyle='--', 
            label=f'Mean: {df["interest_score"].mean():.1f}')
plt.legend()

# Box plot
plt.subplot(1, 2, 2)
plt.boxplot(df['interest_score'], vert=True, patch_artist=True,
            boxprops=dict(facecolor='#3498db', alpha=0.7),
            medianprops=dict(color='red', linewidth=2))
plt.ylabel('Interest Score', fontsize=12)
plt.title('Interest Score Distribution', fontsize=14, fontweight='bold')
plt.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.show()

print(f"📊 Mean Interest Score: {df['interest_score'].mean():.2f}")
print(f"📊 Median Interest Score: {df['interest_score'].median():.2f}")
print(f"📊 Std Dev: {df['interest_score'].std():.2f}")

# %%
# Cell 5: Supply vs Demand Scatter Plot
"""
The KEY visualization: showing the relationship between demand and supply
This is where you can visually see the arbitrage opportunities
"""
plt.figure(figsize=(14, 8))

# Create scatter plot with color coding by opportunity score
scatter = plt.scatter(df['total_supply'], 
                     df['interest_score'],
                     c=df['opportunity_score'],
                     s=200,
                     alpha=0.6,
                     cmap='RdYlGn',
                     edgecolors='black',
                     linewidth=1.5)

# Add labels for each point
for idx, row in df.iterrows():
    plt.annotate(row['keyword'], 
                (row['total_supply'], row['interest_score']),
                xytext=(5, 5),
                textcoords='offset points',
                fontsize=9,
                alpha=0.8)

plt.xlabel('Total Supply (Number of Products)', fontsize=13, fontweight='bold')
plt.ylabel('Interest Score (Search Demand)', fontsize=13, fontweight='bold')
plt.title('Dropshipping Opportunity Map: Demand vs Supply', 
          fontsize=16, fontweight='bold', pad=20)

# Add quadrant lines
plt.axhline(y=50, color='gray', linestyle='--', alpha=0.5, linewidth=1)
plt.axvline(x=250, color='gray', linestyle='--', alpha=0.5, linewidth=1)

# Add quadrant labels
plt.text(100, 90, 'IDEAL ZONE\n(High Demand, Low Supply)', 
         fontsize=11, color='green', fontweight='bold', ha='center',
         bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))
plt.text(400, 90, 'Crowded Market\n(High Demand, High Supply)', 
         fontsize=11, color='orange', fontweight='bold', ha='center',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.3))
plt.text(100, 20, 'Niche Market\n(Low Demand, Low Supply)', 
         fontsize=11, color='blue', fontweight='bold', ha='center',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
plt.text(400, 20, 'Avoid Zone\n(Low Demand, High Supply)', 
         fontsize=11, color='red', fontweight='bold', ha='center',
         bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.3))

# Add colorbar
cbar = plt.colorbar(scatter)
cbar.set_label('Opportunity Score', fontsize=12, fontweight='bold')

plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# %%
# Cell 6: Top 10 Opportunities Bar Chart
"""
Visualize the top opportunities ranked by score
"""
top_10 = df.nlargest(10, 'opportunity_score')

plt.figure(figsize=(14, 8))
bars = plt.barh(range(len(top_10)), top_10['opportunity_score'], 
                color=['#2ecc71' if x > 1.0 else '#f39c12' if x > 0.5 else '#e74c3c' 
                       for x in top_10['opportunity_score']],
                edgecolor='black',
                linewidth=1.2)

plt.yticks(range(len(top_10)), top_10['keyword'], fontsize=11)
plt.xlabel('Opportunity Score', fontsize=13, fontweight='bold')
plt.title('Top 10 Dropshipping Opportunities (Ranked)', fontsize=16, fontweight='bold', pad=20)
plt.grid(axis='x', alpha=0.3)

# Add score labels on bars
for i, (idx, row) in enumerate(top_10.iterrows()):
    plt.text(row['opportunity_score'] + 0.02, i, 
             f"{row['opportunity_score']:.2f}",
             va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.show()

# %%
# Cell 7: Correlation Analysis
"""
Analyze correlations between variables
"""
# Select numeric columns
numeric_cols = ['interest_score', 'total_supply', 'opportunity_score']
correlation_df = df[numeric_cols].corr()

plt.figure(figsize=(8, 6))
sns.heatmap(correlation_df, annot=True, cmap='coolwarm', center=0,
            square=True, linewidths=2, cbar_kws={"shrink": 0.8},
            fmt='.3f', annot_kws={'size': 12, 'weight': 'bold'})
plt.title('Correlation Matrix', fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.show()

print("\n📊 Key Insights:")
print(f"• Interest vs Supply correlation: {correlation_df.loc['interest_score', 'total_supply']:.3f}")
print(f"• Interest vs Opportunity correlation: {correlation_df.loc['interest_score', 'opportunity_score']:.3f}")
print(f"• Supply vs Opportunity correlation: {correlation_df.loc['total_supply', 'opportunity_score']:.3f}")

# %%
# Cell 8: Market Status Distribution
"""
Show distribution of market statuses
"""
if 'market_status' in df.columns:
    status_counts = df['market_status'].value_counts()
    
    plt.figure(figsize=(10, 6))
    colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
    plt.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%',
            startangle=90, colors=colors, textprops={'fontsize': 11, 'weight': 'bold'},
            explode=[0.1 if 'Underserved' in label else 0 for label in status_counts.index])
    plt.title('Market Status Distribution', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.show()

# %%
# Cell 9: Generate Insights Report
"""
Create a text-based insights summary
"""
print("\n" + "="*70)
print("🎯 AUTOMATED INSIGHTS REPORT")
print("="*70 + "\n")

# Calculate key metrics
avg_interest = df['interest_score'].mean()
avg_supply = df['total_supply'].mean()
avg_score = df['opportunity_score'].mean()

strong_buys = df[df['opportunity_score'] > 1.0]
underserved = df[df['total_supply'] < 50]

print(f"📊 Dataset Size: {len(df)} products analyzed")
print(f"📈 Average Interest Score: {avg_interest:.1f}/100")
print(f"📦 Average Supply: {avg_supply:.0f} products")
print(f"⚡ Average Opportunity Score: {avg_score:.3f}")
print(f"\n🚀 Strong Buy Recommendations: {len(strong_buys)} products")
print(f"⭐ Underserved Markets (<50 products): {len(underserved)} products")

if len(strong_buys) > 0:
    print(f"\n💎 TOP OPPORTUNITY:")
    top = strong_buys.iloc[0]
    print(f"   • Product: {top['keyword']}")
    print(f"   • Interest: {top['interest_score']}/100")
    print(f"   • Supply: {top['total_supply']} products")
    print(f"   • Score: {top['opportunity_score']:.3f}")

print("\n" + "="*70)