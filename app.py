import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from utils import fetch_stock_data, create_sequences
from lstm_model import load_trained_model, load_scaler, predict_future_price
import pandas as pd
import numpy as np

# Get the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'frontend', 'templates'),
            static_folder=os.path.join(BASE_DIR, 'frontend', 'static'))
CORS(app)

# Load model and scaler once at startup
try:
    model = load_trained_model()
    scaler = load_scaler()
    print("✅ Model and scaler loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model/scaler: {e}")
    model = None
    scaler = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if model is None or scaler is None:
        return jsonify({'error': 'Model not loaded properly'}), 500
        
    data = request.get_json()
    ticker = data.get('ticker')
    target_date = data.get('date')

    try:
        if not ticker or not target_date:
            return jsonify({'error': 'Ticker and date are required'}), 400

        df = fetch_stock_data(ticker, target_date)

        if df is None or df.empty:
            return jsonify({'error': 'No data found for given ticker and date'}), 400

        required_cols = ['Close', 'SMA_20', 'EMA_20']
        for col in required_cols:
            if col not in df.columns:
                return jsonify({'error': f'Missing column: {col}'}), 400

        features = df[required_cols].values
        scaled = scaler.transform(features)
        x_input = create_sequences(scaled)[-1:]
        predicted_scaled = predict_future_price(model, x_input)
        predicted_price = scaler.inverse_transform([[predicted_scaled, 0, 0]])[0][0]

        last_close = df['Close'].iloc[-1].item()

        pct_change = (predicted_price - last_close) / last_close
        threshold = 0.01
        if pct_change > threshold:
            signal = "Buy"
        elif pct_change < -threshold:
            signal = "Sell"
        else:
            signal = "Hold"

        return jsonify({
            'predicted_price': round(predicted_price, 2),
            'signal': signal,
            'pct_change': round(pct_change * 100, 2),
            'last_close': round(last_close, 2),
            'dates': list(df.index.strftime('%Y-%m-%d')),
            'close': df['Close'].values.tolist(),
            'sma20': df['SMA_20'].values.tolist(),
            'ema20': df['EMA_20'].values.tolist(),
            'predicted_point': {
                'date': df.index[-1].strftime('%Y-%m-%d'),
                'price': round(predicted_price, 2)
            }
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
