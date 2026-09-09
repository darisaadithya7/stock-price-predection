# backend/app.py

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from utils import fetch_stock_data, create_sequences
from lstm_model import load_trained_model, load_scaler, predict_future_price
import pandas as pd
import numpy as np
import os

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
CORS(app)

# Load model and scaler once at startup
model = load_trained_model()
scaler = load_scaler()

# Serve frontend
@app.route('/')
def home():
    return render_template('index.html')

# Prediction API
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    ticker = data.get('ticker')
    target_date = data.get('date')

    try:
        # Validate inputs
        if not ticker or not target_date:
            return jsonify({'error': 'Ticker and date are required'}), 400

        df = fetch_stock_data(ticker, target_date)

        # Check for empty data
        if df is None or df.empty:
            return jsonify({'error': 'No data found for given ticker and date'}), 400

        # Validate required columns
        required_cols = ['Close', 'SMA_20', 'EMA_20']
        for col in required_cols:
            if col not in df.columns:
                return jsonify({'error': f'Missing column: {col}'}), 400

        # Preprocess and predict
        features = df[required_cols].values
        scaled = scaler.transform(features)
        x_input = create_sequences(scaled)[-1:]
        predicted_scaled = predict_future_price(model, x_input)
        predicted_price = scaler.inverse_transform([[predicted_scaled, 0, 0]])[0][0]

        # Safely extract last close
        # ✅ Fixed line
        # Safely extract last close
        last_close = df['Close'].iloc[-1].item()

        # Calculate percent change and set three-tier signal
        pct_change = (predicted_price - last_close) / last_close
        threshold = 0.01  # 1%
        if pct_change > threshold:
            signal = "Buy"
        elif pct_change < -threshold:
            signal = "Sell"
        else:
            signal = "Hold"
       

        return jsonify({
            'predicted_price': round(predicted_price, 2),
            'signal': signal,
            'pct_change': round(pct_change * 100, 2),      # ← new
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
        print("ERROR:", str(e))  # show exact cause in terminal
        return jsonify({'error': str(e)}), 400

# Run locally
if __name__ == '__main__':
    app.run(debug=True)
