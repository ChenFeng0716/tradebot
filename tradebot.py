import time
import pandas as pd
import requests
import streamlit as st

# CryptoCompare API endpoints
BASE_URL = "https://min-api.cryptocompare.com/data/"
HISTO_DAY_URL = BASE_URL + "histoday"
PAIR = "BTC/USDT"
LIMIT = 200

# Define strategy parameters
short_window = 50
long_window = 200

# Initial account balance (for demonstration)
account_balance = 10000  # USDT

# Streamlit setup
st.title("Crypto Trading Bot Simulation")
st.sidebar.title("Bot Settings")

# User-defined settings
bot_speed = st.sidebar.slider("Bot Speed (seconds)", 1, 60, 10)
initial_balance = st.sidebar.number_input("Initial Account Balance (USDT)", min_value=1, value=10000)
pair = st.sidebar.text_input("Trading Pair (e.g., BTC/USDT)", value="BTC/USDT")
short_window = st.sidebar.number_input("Short Window (days)", min_value=1, value=50)
long_window = st.sidebar.number_input("Long Window (days)", min_value=1, value=200)

# Display user-defined settings
st.sidebar.subheader("Bot Configuration")
st.sidebar.write(f"Initial Balance: {initial_balance} USDT")
st.sidebar.write(f"Trading Pair: {pair}")
st.sidebar.write(f"Short Window: {short_window} days")
st.sidebar.write(f"Long Window: {long_window} days")

col1, col2 = st.columns(2)
output_area = col1.empty()
start_bot = col1.button("Start Bot")
stop_bot = col2.button("Stop Bot")

def fetch_data(pair, limit):
    params = {
        "fsym": pair.split("/")[0],
        "tsym": pair.split("/")[1],
        "limit": limit,
        "aggregate": 1
    }

    response = requests.get(HISTO_DAY_URL, params=params)
    data = response.json()
    # print(f"response: {data}")
    
    df = pd.DataFrame(data['Data'])
    # print(f"response: {df}")
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    df['close'] = df['close'].astype(float)
    
    return df

def calculate_moving_averages(df, short_window, long_window):
    df['SMA50'] = df['close'].rolling(window=short_window).mean()
    df['SMA200'] = df['close'].rolling(window=long_window).mean()
    return df

def execute_order(order_type, price, quantity):
    global account_balance
    
    if order_type == 'buy':
        st.write(f"Executing BUY order at price {price}, quantity {quantity}")
        account_balance -= price * quantity
        st.write(f"Updated account balance: {account_balance} USDT")
    
    elif order_type == 'sell':
        st.write(f"Executing SELL order at price {price}, quantity {quantity}")
        account_balance += price * quantity
        st.write(f"Updated account balance: {account_balance} USDT")

def main():
     while start_bot:
        # Fetch and preprocess data
        data = fetch_data(pair, LIMIT)
        data = calculate_moving_averages(data, short_window, long_window)

        st.write(f"Data fetched at {data.index[-1]}")
        st.write(f"SMA50: {data['SMA50'].iloc[-1]}, SMA200: {data['SMA200'].iloc[-1]}")

        # Implement a simple crossover strategy
        if data['SMA50'].iloc[-2] < data['SMA200'].iloc[-2] and data['SMA50'].iloc[-1] >= data['SMA200'].iloc[-1]:
            st.write(f"Buy signal at {data.index[-1]}")
            # Hypothetical buy order
            execute_order('buy', data['close'].iloc[-1], 1)
        
        elif data['SMA50'].iloc[-2] > data['SMA200'].iloc[-2] and data['SMA50'].iloc[-1] <= data['SMA200'].iloc[-1]:
            st.write(f"Sell signal at {data.index[-1]}")
            # Hypothetical sell order
            execute_order('sell', data['close'].iloc[-1], 1)
        
        else:
            st.write("Hold")  # Neither buy nor sell conditions met
        
        time.sleep(bot_speed)  # Sleep for user-defined seconds

if __name__ == '__main__':
    main()
    if stop_bot:  # Stop the bot when the "Stop Bot" button is pressed
        output_area.text("Bot stopped.")

# revised by Chen, 2025.1