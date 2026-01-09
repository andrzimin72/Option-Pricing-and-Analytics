# app.py

from flask import Flask, request, jsonify
from pricing_engine import BSMAnalytical, implied_volatility, baw_american_call, baw_american_put
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)  # ← FIXED: was "__ (__name__)" before
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

def validate_float(value, name, min_val=None, max_val=None):
    try:
        x = float(value)
        if min_val is not None and x < min_val:
            raise ValueError(f"{name} must be >= {min_val}")
        if max_val is not None and x > max_val:
            raise ValueError(f"{name} must be <= {max_val}")
        return x
    except (TypeError, ValueError) as e:
        raise ValueError(f"Invalid {name}: {e}")

@app.route('/price', methods=['POST'])
def price_option():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON body required"}), 400

        S = validate_float(data.get('S'), 'S', min_val=0.01)
        K = validate_float(data.get('K'), 'K', min_val=0.01)
        T = validate_float(data.get('T'), 'T', min_val=1e-6, max_val=10.0)
        r = validate_float(data.get('r', 0.0), 'r', min_val=-1.0, max_val=1.0)
        sigma = validate_float(data.get('sigma', 0.2), 'sigma', min_val=1e-6, max_val=5.0)
        c = validate_float(data.get('c', 0.0), 'c', min_val=0.0, max_val=1.0)
        option_type = str(data.get('option_type', 'call')).lower()
        model = str(data.get('model', 'bsm')).lower()

        if option_type not in ('call', 'put'):
            return jsonify({"error": "option_type must be 'call' or 'put'"}), 400
        if model not in ('bsm', 'baw'):
            return jsonify({"error": "model must be 'bsm' or 'baw'"}), 400

        if model == 'bsm':
            bsm = BSMAnalytical(S, K, T, r, sigma, c, option_type)
            price = bsm.price()
            greeks = {k: v for k, v in bsm.all_greeks().items() if k != 'Price'}
        else:
            if option_type == 'call':
                price = baw_american_call(S, K, T, r, sigma, c)
            else:
                price = baw_american_put(S, K, T, r, sigma, c)
            greeks = {}

        return jsonify({
            "price": round(price, 6),
            "greeks": {k: round(v, 6) for k, v in greeks.items()}
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/implied_vol', methods=['POST'])
def implied_vol():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON body required"}), 400

        S = validate_float(data.get('S'), 'S', min_val=0.01)
        K = validate_float(data.get('K'), 'K', min_val=0.01)
        T = validate_float(data.get('T'), 'T', min_val=1e-6, max_val=10.0)
        r = validate_float(data.get('r', 0.0), 'r', min_val=-1.0, max_val=1.0)
        c = validate_float(data.get('c', 0.0), 'c', min_val=0.0, max_val=1.0)
        mp = validate_float(data.get('market_price'), 'market_price', min_val=0.0)
        option_type = str(data.get('option_type', 'call')).lower()

        if option_type not in ('call', 'put'):
            return jsonify({"error": "option_type must be 'call' or 'put'"}), 400

        iv = implied_volatility(mp, S, K, T, r, c, option_type)
        return jsonify({"implied_volatility": round(iv, 6)})

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"IV error: {e}")
        return jsonify({"error": "Failed to compute implied volatility"}), 500

# Only for local dev (won't run under Gunicorn)
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)