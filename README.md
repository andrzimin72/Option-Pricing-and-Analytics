# Option-Pricing-and-Analytics

This is a complete option pricing and analytics platform. Now we have four integrated components that work together:

## 1. pricing_engine.py - the Brain

This is a library of mathematical models for option pricing. Contains:
- Black-Scholes-Merton (BSM): Exact European option prices + Greeks;
- Barone-Adesi-Whaley (BAW): Fast approximation for American options;
- Implied Volatility Solver: Finds σ from market price;
- Binomial & Trinomial Trees: High-accuracy numerical methods for American/Bermudan options.
This is our core quant engine.

## 2. vectorized.py + example_usage.py - the Analyst

This is a batch processing toolkit for research and calibration. Does:
- price hundreds of options at once (across strikes/maturities);
- compute Greeks for entire surfaces;
- calibrate implied volatility smiles/skews from market data;
- export results to CSV for Excel, Python, or R.

Used for:
- risk analysis;
- strategy backtesting;
- volatility surface modeling;
- academic or proprietary research.

## 3. app.py + Gunicorn - the API Server

This is a real-time pricing microservice. Does:
- accept JSON requests (e.g., from a trading desk or web app);
- return instant prices & Greeks (BSM or BAW);
- safely handle errors, validate inputs, log activity.

Used for:
- real-time trading systems;
- web dashboards;
- mobile apps;
- integration with Excel/Python via HTTP.

## 4. visualize.py - creates separate PNG files for each indicator:

- option_price_surface.png - price heatmap;
- delta_surface.png - Delta (RdBu: blue=long, red=short);
- gamma_surface.png - Gamma (YlOrRd: yellow=low, red=high);
- vega_surface.png - Vega (Purples: intuitive for vol);
- theta_surface.png - Theta (Blues_r: darker = faster decay);
- rho_surface.png - Rho (Greens: interest rate sensitivity);
- volatility_smile.png - IV curve;
- all_greeks_vs_strike.png - All Greeks on one plot.

## 5. requirements.txt - the Blueprint

This is a list of all dependencies. Ensures anyone (or any server) can reproduce our environment exactly.

## How to Run:

1. Install Dependencies
pip install -r requirements.txt

2. Run Analysis (Generates CSVs)
python3 example_usage.py

Outputs: bsm_pricing_with_greeks.csv, implied_volatilities.csv

3. Start the API (Real-Time Pricing)

A. Start Gunicorn (Production Server)
gunicorn -w 2 -b 127.0.0.1:5000 app:app

You’ll see: [INFO] Listening at: http://127.0.0.1:5000

B. Test the API
In another terminal, run:

Price an option:
curl -s http://127.0.0.1:5000/price \
   -X POST \
   -H "Content-Type: application/json" \
   -d '{"S":100,"K":110,"T":0.25,"r":0.02,"sigma":0.3,"option_type":"put","model":"bsm"}'

Get implied volatility:
curl -s http://127.0.0.1:5000/implied_vol \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"S":100,"K":110,"T":0.25,"r":0.02,"market_price":12.085444,"option_type":"put"}'

4: Keep API Running (Optional)

A: Run in Background
#Stop Gunicorn (Ctrl+C), then:
 nohup gunicorn -w 2 -b 127.0.0.1:5000 app:app > api.log 2>&1 &

B: Auto-Start on Boot (Recommended for servers)
#Create service file
sudo nano /etc/systemd/system/option-pricer.service

Then:
sudo systemctl daemon-reload
sudo systemctl enable option-pricer
sudo systemctl start option-pricer

Check status:
sudo systemctl status option-pricer

To Stop Everything

Analysis: Just close the terminal after example_usage.py finishes.
API:
If running in foreground: Ctrl + C;
If running via nohup: pkill -f gunicorn;
If using systemd: sudo systemctl stop option-pricer.

We’re all set:
- for analysis: python3 example_usage.py - CSVs;
- for real-time pricing: gunicorn app:app - call via curl or code;
- for 24/7 server: use system.

This is everything we need to run, test, and deploy this system. It’s system integrated components that work together:
- for real-time use - our API calls the pricing engine;
- for research - our analysis scripts call the pricing engine, then save to CSV;
- everything shares the same models - consistent results everywhere.

## Recommendations

I think these scripts could be used to:
- real-time pricing of OTC options via API;
- compute Greeks for portfolio sensitivity;
- calibrate IV surfaces from market data;
- test pricing models, compare trees vs. BAW;
- build client-facing tool;
- teach options, Greeks, and numerical methods.

I suppose that key strengths of this system are:
- accuracy: Uses industry-standard models (BSM, BAW, binomial);
- speed: BSM/BAW for real-time, trees for high precision;
- flexibility: supports european, american, and custom exercise;
- production-ready: secure, validated, logged, scalable.
