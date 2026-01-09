# pricing_engine.py

import math
import numpy as np
from scipy.stats import norm

class BSMAnalytical:
    def __init__(self, S, K, T, r, sigma, c, option_type='call'):
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.c = c
        self.option_type = option_type.lower()
        if self.option_type not in ('call', 'put'):
            raise ValueError("option_type must be 'call' or 'put'")
        if T <= 0 or sigma <= 0:
            raise ValueError("T and sigma must be positive")

    def _d1_d2(self):
        sigma_sqrt_T = self.sigma * math.sqrt(self.T)
        d1 = (math.log(self.S / self.K) + (self.r - self.c + 0.5 * self.sigma**2) * self.T) / sigma_sqrt_T
        d2 = d1 - sigma_sqrt_T
        return d1, d2

    def price(self):
        d1, d2 = self._d1_d2()
        if self.option_type == 'call':
            return self.S * math.exp(-self.c * self.T) * norm.cdf(d1) - self.K * math.exp(-self.r * self.T) * norm.cdf(d2)
        else:
            return self.K * math.exp(-self.r * self.T) * norm.cdf(-d2) - self.S * math.exp(-self.c * self.T) * norm.cdf(-d1)

    def delta(self):
        d1, _ = self._d1_d2()
        if self.option_type == 'call':
            return math.exp(-self.c * self.T) * norm.cdf(d1)
        else:
            return -math.exp(-self.c * self.T) * norm.cdf(-d1)

    def gamma(self):
        d1, _ = self._d1_d2()
        return (math.exp(-self.c * self.T) * norm.pdf(d1)) / (self.S * self.sigma * math.sqrt(self.T))

    def vega(self):
        d1, _ = self._d1_d2()
        return self.S * math.exp(-self.c * self.T) * norm.pdf(d1) * math.sqrt(self.T)

    def theta(self):
        d1, d2 = self._d1_d2()
        if self.option_type == 'call':
            term1 = -(self.S * math.exp(-self.c * self.T) * norm.pdf(d1) * self.sigma) / (2 * math.sqrt(self.T))
            term2 = -self.r * self.K * math.exp(-self.r * self.T) * norm.cdf(d2)
            term3 = self.c * self.S * math.exp(-self.c * self.T) * norm.cdf(d1)
            return term1 + term2 + term3
        else:
            term1 = -(self.S * math.exp(-self.c * self.T) * norm.pdf(d1) * self.sigma) / (2 * math.sqrt(self.T))
            term2 = self.r * self.K * math.exp(-self.r * self.T) * norm.cdf(-d2)
            term3 = -self.c * self.S * math.exp(-self.c * self.T) * norm.cdf(-d1)
            return term1 + term2 + term3

    def rho(self):
        _, d2 = self._d1_d2()
        if self.option_type == 'call':
            return self.K * self.T * math.exp(-self.r * self.T) * norm.cdf(d2)
        else:
            return -self.K * self.T * math.exp(-self.r * self.T) * norm.cdf(-d2)

    def all_greeks(self):
        return {
            "Price": self.price(),
            "Delta": self.delta(),
            "Gamma": self.gamma(),
            "Vega (per 1.0 vol)": self.vega(),
            "Vega (per 1% vol)": self.vega() * 0.01,
            "Theta (annual)": self.theta(),
            "Theta (per day)": self.theta() / 365.0,
            "Rho (per 1.0 rate)": self.rho(),
            "Rho (per 1% rate)": self.rho() * 0.01,
        }

def implied_volatility(market_price, S, K, T, r, c, option_type='call', tol=1e-8, max_iter=100):
    if market_price < 0:
        raise ValueError("Market price must be non-negative")
    
    if option_type == 'call':
        intrinsic = max(S * math.exp(-c * T) - K * math.exp(-r * T), 0)
    else:
        intrinsic = max(K * math.exp(-r * T) - S * math.exp(-c * T), 0)
    
    if market_price <= intrinsic:
        return 1e-8

    sigma = 0.2
    for _ in range(max_iter):
        bsm = BSMAnalytical(S, K, T, r, sigma, c, option_type)
        price = bsm.price()
        vega = bsm.vega()
        diff = price - market_price
        if abs(diff) < tol:
            return sigma
        if vega < 1e-8:
            break
        sigma_new = sigma - diff / vega
        if sigma_new < 1e-8 or sigma_new > 5.0:
            break
        sigma = sigma_new

    low, high = 1e-8, 5.0
    for _ in range(max_iter):
        mid = (low + high) / 2
        bsm = BSMAnalytical(S, K, T, r, mid, c, option_type)
        price = bsm.price()
        if abs(price - market_price) < tol:
            return mid
        if price > market_price:
            high = mid
        else:
            low = mid
    return (low + high) / 2

def baw_american_call(S, K, T, r, sigma, c):
    if c >= r:
        bsm = BSMAnalytical(S, K, T, r, sigma, c, 'call')
        return bsm.price()
    q2 = (- (r - c - sigma**2/2) + math.sqrt((r - c - sigma**2/2)**2 + 2 * r * sigma**2)) / sigma**2
    S_star = K / (1 - 1/q2)
    if S >= S_star:
        return S - K
    else:
        bsm = BSMAnalytical(S, K, T, r, sigma, c, 'call')
        european = bsm.price()
        d1 = (math.log(S/K) + (r - c + sigma**2/2)*T) / (sigma * math.sqrt(T))
        A2 = (S_star / q2) * (1 - math.exp(-c * T) * norm.cdf(d1 + sigma * math.sqrt(T)))
        return european + A2 * (S / S_star)**q2

def baw_american_put(S, K, T, r, sigma, c):
    q1 = (- (r - c - sigma**2/2) - math.sqrt((r - c - sigma**2/2)**2 + 2 * r * sigma**2)) / sigma**2
    S_star = K / (1 - 1/q1)
    if S <= S_star:
        return K - S
    else:
        bsm = BSMAnalytical(S, K, T, r, sigma, c, 'put')
        european = bsm.price()
        d1 = (math.log(S/K) + (r - c + sigma**2/2)*T) / (sigma * math.sqrt(T))
        A1 = (-S_star / q1) * (1 - math.exp(-c * T) * norm.cdf(-(d1 + sigma * math.sqrt(T))))
        return european + A1 * (S / S_star)**q1

# -------------------------------------------------
# Binomial Tree
# -------------------------------------------------
class BinomialTree:
    def __init__(self, T, S0, r, sigma, c, K, n, option_type='call'):
        self.T, self.S0, self.r, self.sigma, self.c, self.K, self.n = T, S0, r, sigma, c, K, n
        self.option_type = option_type.lower()
        self.dt = T / n
        self.u = math.exp(sigma * math.sqrt(self.dt))
        self.d = 1.0 / self.u
        self.q = (math.exp((r - c) * self.dt) - self.d) / (self.u - self.d)
        self.R = math.exp(r * self.dt)

        self.stock_tree = np.zeros((n + 1, n + 1))
        self.stock_tree[0, 0] = S0
        for i in range(1, n + 1):
            self.stock_tree[0, i] = self.stock_tree[0, i - 1] * self.u
            for j in range(1, i + 1):
                self.stock_tree[j, i] = self.stock_tree[j - 1, i - 1] * self.d

    def _intrinsic(self, S):
        return max(S - self.K, 0) if self.option_type == 'call' else max(self.K - S, 0)

    def price(self, exercise_style='american'):
        payoff = np.array([self._intrinsic(self.stock_tree[j, self.n]) for j in range(self.n + 1)])
        option = payoff.copy()
        for i in range(self.n - 1, -1, -1):
            for j in range(i + 1):
                cont = (self.q * option[j] + (1 - self.q) * option[j + 1]) / self.R
                if exercise_style == 'american':
                    ex = self._intrinsic(self.stock_tree[j, i])
                    option[j] = max(cont, ex)
                else:
                    option[j] = cont
        return option[0]

# -------------------------------------------------
# Trinomial Tree
# -------------------------------------------------
class TrinomialTree:
    def __init__(self, T, S0, r, sigma, c, K, n, option_type='call'):
        self.T, self.S0, self.r, self.sigma, self.c, self.K, self.n = T, S0, r, sigma, c, K, n
        self.option_type = option_type.lower()
        self.dt = T / n
        self.dr = sigma * math.sqrt(3 * self.dt)
        self.p_u = 1/6 + ((r - c - 0.5 * sigma**2) * math.sqrt(self.dt)) / (2 * sigma * math.sqrt(3))
        self.p_d = 1/6 - ((r - c - 0.5 * sigma**2) * math.sqrt(self.dt)) / (2 * sigma * math.sqrt(3))
        self.p_m = 1 - self.p_u - self.p_d
        self.p_u, self.p_d = max(self.p_u, 0), max(self.p_d, 0)
        self.p_m = 1 - self.p_u - self.p_d
        self.R = math.exp(r * self.dt)

    def _intrinsic(self, S):
        return max(S - self.K, 0) if self.option_type == 'call' else max(self.K - S, 0)

    def price(self, exercise_style='american'):
        m = 2 * self.n + 1
        lnS0 = math.log(self.S0)
        stock = np.array([math.exp(lnS0 + (i - self.n) * self.dr) for i in range(m)])
        option = np.array([self._intrinsic(s) for s in stock])

        for step in range(self.n - 1, -1, -1):
            m_curr = 2 * step + 1
            new_option = np.zeros(m_curr)
            for i in range(m_curr):
                j = i - step
                S = math.exp(lnS0 + j * self.dr)
                idx_base = step + 1
                idx_up = (j + 1) + idx_base
                idx_mid = j + idx_base
                idx_down = (j - 1) + idx_base
                cont = (self.p_u * option[idx_up] + self.p_m * option[idx_mid] + self.p_d * option[idx_down]) / self.R
                if exercise_style == 'american':
                    ex = self._intrinsic(S)
                    new_option[i] = max(cont, ex)
                else:
                    new_option[i] = cont
            option = new_option
        return option[0]