import streamlit as st
import pandas as pd
import requests

# Set up the page
st.set_page_config(page_title="Getting BREAKOUT Data", page_icon="💰")

@st.cache_data
def fetch_binance_usdt_pairs():
    url = "https://api.binance.com/api/v3/ticker/price"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        usdt_pairs = [item['symbol'] for item in data if 'USDT' in item['symbol']]
        return usdt_pairs
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from Binance: {e}")
        return []

@st.cache_data
def fetch_binance_historical_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1d&limit=30"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data, columns=["Timestamp", "Open", "High", "Low", "Close", "Volume", "CloseTime",
                                         "QuoteAssetVolume", "NumberOfTrades", "TakerBuyBaseAssetVolume",
                                         "TakerBuyQuoteAssetVolume", "Ignore"])
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        df['Close'] = pd.to_numeric(df['Close'])
        return df[['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']]
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching historical data for {symbol}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error

def main():
    pairs = fetch_binance_usdt_pairs()

    if not pairs:
        st.warning("No trading pairs found or there was an error fetching them.")
        return

    # Create a sidebar for user selection
    st.sidebar.header("Select Trading Pair")
    selected_pair = st.sidebar.selectbox("Choose a pair:", pairs)
    
    # Fetch historical data for the selected pair
    historical_data = fetch_binance_historical_data(selected_pair)

    # Display the selected trading pair
    st.title(f"Historical Data for {selected_pair}")
    
    if not historical_data.empty:
        # Show the data in a table
        st.write(historical_data)

        # Optional: Plotting the closing prices
        st.line_chart(historical_data.set_index('Timestamp')['Close'])
    else:
        st.warning("No historical data available for this trading pair.")

if __name__ == "__main__":
    main()


