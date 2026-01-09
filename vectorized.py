# vectorized.py

import numpy as np
import pandas as pd
from typing import List
from pricing_engine import (
    BSMAnalytical,
    baw_american_call,
    baw_american_put,
    implied_volatility,
    BinomialTree,
    TrinomialTree
)

def price_vectorized_with_greeks(
    model: str,
    S: float,
    K_list: List[float],
    T_list: List[float],
    r: float,
    sigma: float,
    c: float,
    option_type: str = 'call',
    exercise_style: str = 'american',
    n_steps: int = 100,
    include_greeks: bool = False
) -> pd.DataFrame:
    results = []
    K_grid, T_grid = np.meshgrid(K_list, T_list, indexing='ij')
    
    for i in range(len(K_list)):
        for j in range(len(T_list)):
            K = K_grid[i, j]
            T = T_grid[i, j]
            
            if T <= 0:
                price = max(K - S, 0) if option_type == 'put' else max(S - K, 0)
                greeks = {}
            else:
                try:
                    if model == 'bsm':
                        bsm = BSMAnalytical(S, K, T, r, sigma, c, option_type)
                        price = bsm.price()
                        greeks = bsm.all_greeks() if include_greeks else {}
                        if include_greeks:
                            greeks.pop('Price', None)
                    elif model == 'baw':
                        if option_type == 'call':
                            price = baw_american_call(S, K, T, r, sigma, c)
                        else:
                            price = baw_american_put(S, K, T, r, sigma, c)
                        greeks = {}
                    elif model == 'binomial':
                        tree = BinomialTree(T, S, r, sigma, c, K, n_steps, option_type)
                        price = tree.price(exercise_style=exercise_style)
                        greeks = {}
                    elif model == 'trinomial':
                        tree = TrinomialTree(T, S, r, sigma, c, K, n_steps, option_type)
                        price = tree.price(exercise_style=exercise_style)
                        greeks = {}
                    else:
                        raise ValueError(f"Unknown model: {model}")
                except Exception as e:
                    price = np.nan
                    greeks = {}
                    print(f"Error pricing K={K}, T={T}: {e}")
            
            row = {
                'Strike': K,
                'Maturity': T,
                'Price': price,
                'Model': model,
                'Style': exercise_style if model in ['binomial', 'trinomial'] else 'european'
            }
            if include_greeks:
                for g in ['Delta', 'Gamma', 'Vega (per 1% vol)', 'Theta (per day)', 'Rho (per 1% rate)']:
                    row[g] = greeks.get(g, np.nan)
            results.append(row)
    
    return pd.DataFrame(results)

def calibrate_implied_volatilities(
    S: float,
    K_list: List[float],
    T: float,
    r: float,
    c: float,
    market_prices: List[float],
    option_type: str = 'call'
) -> pd.DataFrame:
    if len(K_list) != len(market_prices):
        raise ValueError("K_list and market_prices must have same length")
    
    results = []
    for K, mp in zip(K_list, market_prices):
        try:
            iv = implied_volatility(mp, S, K, T, r, c, option_type) if mp > 0 else np.nan
        except:
            iv = np.nan
        results.append({'Strike': K, 'MarketPrice': mp, 'ImpliedVol': iv})
    return pd.DataFrame(results)