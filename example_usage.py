# example_usage.py

import pandas as pd
from vectorized import price_vectorized_with_greeks, calibrate_implied_volatilities

# Parameters
S = 100
r = 0.02
c = 0.01
sigma = 0.3
option_type = 'put'
K_list = [90, 100, 110, 120]
T_list = [0.25, 0.5]

# Price with BSM + Greeks
df = price_vectorized_with_greeks(
    model='bsm',
    S=S, K_list=K_list, T_list=T_list,
    r=r, sigma=sigma, c=c,
    option_type=option_type,
    include_greeks=True
)
print("BSM Pricing Results:")
print(df)
df.to_csv("bsm_pricing_with_greeks.csv", index=False)

# Implied volatility calibration
market_prices = [1.2, 3.5, 8.9, 15.1]  # example market prices
iv_df = calibrate_implied_volatilities(
    S=S, K_list=K_list, T=0.25,
    r=r, c=c, market_prices=market_prices,
    option_type=option_type
)
print("\nImplied Volatilities:")
print(iv_df)
iv_df.to_csv("implied_volatilities.csv", index=False)

print("\n✅ Results saved to CSV!")