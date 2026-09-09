# backend/train_only_once.py
from utils import fetch_stock_data, scale_data, create_sequences
from lstm_model import train_and_save_model, save_scaler
import pandas as pd

def main():
    ticker = 'AAPL'  # Default for training
    end_date = pd.Timestamp.today().strftime('%Y-%m-%d')
    data = fetch_stock_data(ticker, end_date)
    features = data[['Close', 'SMA_20', 'EMA_20']].values
    scaled, scaler = scale_data(features)
    sequences = create_sequences(scaled)
    x_train = sequences
    y_train = scaled[60:, 0]  # target: close price
    train_and_save_model(x_train, y_train)
    save_scaler(scaler)

if __name__ == "__main__":
    main()
