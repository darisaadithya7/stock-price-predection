# backend/lstm_model.py

import os
import numpy as np
import joblib
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout

# ✅ FIXED paths — assumes files are in backend/
MODEL_PATH = 'model.h5'
SCALER_PATH = 'scaler.pkl'

def build_model(input_shape):
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
    model.add(Dropout(0.2))
    model.add(LSTM(50))
    model.add(Dropout(0.2))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def train_and_save_model(x_train, y_train):
    model = build_model((x_train.shape[1], x_train.shape[2]))
    model.fit(x_train, y_train, epochs=500, batch_size=64, verbose=1)
    model.save(MODEL_PATH)

def load_trained_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    return load_model(MODEL_PATH)

def save_scaler(scaler):
    joblib.dump(scaler, SCALER_PATH)

def load_scaler():
    if not os.path.exists(SCALER_PATH):
        raise FileNotFoundError(f"Scaler file not found at {SCALER_PATH}")
    return joblib.load(SCALER_PATH)

def predict_future_price(model, input_sequence):
    input_seq = np.expand_dims(input_sequence[-1], axis=0)
    prediction = model.predict(input_seq, verbose=0)
    return prediction[0][0]
