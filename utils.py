# backend/utils.py
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

def fetch_stock_data(ticker, end_date, period='1y'):
    data = yf.download(ticker, end=end_date, period=period)
    if data.empty:
        raise ValueError("No data found. Please check the ticker or date.")
    data = data[['Close']]
    data['SMA_20'] = data['Close'].rolling(window=20).mean()
    data['EMA_20'] = data['Close'].ewm(span=20, adjust=False).mean()
    data.dropna(inplace=True)
    return data

def scale_data(data):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(data)
    return scaled, scaler

def create_sequences(data, seq_length=60):
    x = []
    for i in range(seq_length, len(data)):
        x.append(data[i-seq_length:i])
    return np.array(x)
