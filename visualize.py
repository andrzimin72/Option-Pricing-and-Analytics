# visualize.py
"""
Option Pricing Visualization Tool
Generates separate PNG files for all Greeks + custom color schemes.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Check if CSV files exist
if not os.path.exists('bsm_pricing_with_greeks.csv'):
    print("❌ Error: 'bsm_pricing_with_greeks.csv' not found!")
    print("👉 Run 'python3 example_usage.py' first to generate data.")
    exit(1)

# Set high-resolution output
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300  # Ultra HD for printing
sns.set_theme(style="whitegrid", font_scale=1.1)

# Load pricing data
df = pd.read_csv('bsm_pricing_with_greeks.csv')
print(f"📊 Loaded {len(df)} pricing records")

# Create pivot tables for all Greeks
indicators = {
    'Price': ('Price', 'option_price_surface.png', 'viridis', '.2f'),
    'Delta': ('Delta', 'delta_surface.png', 'RdBu', '.2f'),
    'Gamma': ('Gamma', 'gamma_surface.png', 'YlOrRd', '.4f'),
    'Vega (per 1% vol)': ('Vega (per 1% vol)', 'vega_surface.png', 'Purples', '.4f'),
    'Theta (per day)': ('Theta (per day)', 'theta_surface.png', 'Blues_r', '.4f'),
    'Rho (per 1% rate)': ('Rho (per 1% rate)', 'rho_surface.png', 'Greens', '.4f')
}

# Function to create heatmap
def plot_heatmap(data, title, ylabel, filename, cmap, fmt):
    plt.figure(figsize=(10, 6))
    ax = sns.heatmap(
        data,
        annot=True,
        fmt=fmt,
        cmap=cmap,
        cbar_kws={'shrink': 0.8},
        linewidths=0.3,
        square=False
    )
    plt.title(title, fontsize=14, fontweight='bold', pad=20)
    plt.xlabel('Maturity (Years)', fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {filename}")

# Generate heatmaps for all indicators
for name, (col, filename, cmap, fmt) in indicators.items():
    if col in df.columns:
        matrix = df.pivot(index='Strike', columns='Maturity', values=col)
        plot_heatmap(
            matrix,
            f'{name} Surface (Strike vs Maturity)',
            'Strike',
            filename,
            cmap,
            fmt
        )
    else:
        print(f"⚠️ Warning: '{col}' not found in CSV. Skipping {filename}.")

# 7. Volatility Smile
plt.figure(figsize=(10, 6))
try:
    if os.path.exists('implied_volatilities.csv'):
        iv_df = pd.read_csv('implied_volatilities.csv')
        plt.plot(
            iv_df['Strike'],
            iv_df['ImpliedVol'] * 100,
            'bo-',
            linewidth=2.5,
            markersize=8,
            color='#2E86AB',
            label='Implied Volatility'
        )
        plt.xlabel('Strike', fontsize=12)
        plt.ylabel('Implied Volatility (%)', fontsize=12)
        plt.title('Volatility Smile', fontsize=14, fontweight='bold')
        plt.grid(True, linestyle='--', alpha=0.7)
        if 'sigma' in df.columns and len(df['sigma']) > 0:
            flat_vol = df['sigma'].iloc[0] * 100
            plt.axhline(
                y=flat_vol,
                color='#A23B72',
                linestyle='--',
                alpha=0.8,
                label=f'Flat Vol ({flat_vol:.1f}%)'
            )
        plt.legend()
    else:
        plt.text(0.5, 0.5, 'Volatility Smile Data\nNot Available',
                 ha='center', va='center', transform=plt.gca().transAxes, fontsize=14)
        plt.title('Volatility Smile', fontsize=14, fontweight='bold')
except Exception as e:
    plt.text(0.5, 0.5, f'Error: {str(e)}',
             ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
    plt.title('Volatility Smile', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('volatility_smile.png', bbox_inches='tight')
plt.close()
print("✅ Saved: volatility_smile.png")

# 8. All Greeks vs Strike (at shortest maturity)
maturities = sorted(df['Maturity'].unique())
T_min = maturities[0]
df_short = df[df['Maturity'] == T_min].sort_values('Strike')

plt.figure(figsize=(12, 7))
# Normalize scales for visibility
plt.plot(df_short['Strike'], df_short['Delta'], 'o-', label='Delta', linewidth=2.5, markersize=7, color='#2E86AB')
plt.plot(df_short['Strike'], df_short['Gamma'] * 100, 's-', label='Gamma × 100', linewidth=2.5, markersize=7, color='#A23B72')
plt.plot(df_short['Strike'], df_short['Vega (per 1% vol)'], '^-', label='Vega (per 1%)', linewidth=2.5, markersize=7, color='#F18F01')
plt.plot(df_short['Strike'], df_short['Theta (per day)'] * 100, 'd-', label='Theta/Day × 100', linewidth=2.5, markersize=7, color='#C73E1D')
plt.plot(df_short['Strike'], df_short['Rho (per 1% rate)'], 'p-', label='Rho (per 1%)', linewidth=2.5, markersize=7, color='#5A5A5A')

plt.xlabel('Strike', fontsize=12)
plt.ylabel('Greek Value', fontsize=12)
plt.title(f'All Greeks vs Strike (Maturity = {T_min:.2f} Years)', fontsize=14, fontweight='bold')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('all_greeks_vs_strike.png', bbox_inches='tight')
plt.close()
print("✅ Saved: all_greeks_vs_strike.png")

# Final summary
print("\n✨ All charts saved as high-resolution PNG files!")
print("📁 Files created:")
files = [
    "option_price_surface.png",
    "delta_surface.png",
    "gamma_surface.png",
    "vega_surface.png",
    "theta_surface.png",
    "rho_surface.png",
    "volatility_smile.png",
    "all_greeks_vs_strike.png"
]
for f in files:
    if os.path.exists(f):
        print(f"   - {f}")