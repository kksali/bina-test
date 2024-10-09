import streamlit as st
import pandas as pd
import requests

# Set up the page
st.set_page_config(page_title="Getting BREAKOUT Data", page_icon="💰")

@st.cache_data
@st.cache_data
def fetch_binance_pairs():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        # Check if 'symbols' exists in the response
        if 'symbols' in data:
            usdt_pairs = [symbol['symbol'] for symbol in data['symbols'] if symbol['quoteAsset'] == 'USDT']
            return usdt_pairs
        else:
            st.error("Unexpected response structure: 'symbols' key not found.")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from Binance: {e}")
        return []


@st.cache_data
def fetch_binance_historical_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1d&limit=30"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=["Timestamp", "Open", "High", "Low", "Close", "Volume", "CloseTime",
                                     "QuoteAssetVolume", "NumberOfTrades", "TakerBuyBaseAssetVolume",
                                     "TakerBuyQuoteAssetVolume", "Ignore"])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    df['Close'] = pd.to_numeric(df['Close'])
    return df[['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']]


def main():
    pairs = fetch_binance_pairs()
    
    # Create a sidebar for user selection
    st.sidebar.header("Select Trading Pair")
    selected_pair = st.sidebar.selectbox("Choose a pair:", pairs)
    
    # Fetch historical data for the selected pair
    historical_data = fetch_binance_historical_data(selected_pair)

    # Display the selected trading pair
    st.title(f"Historical Data for {selected_pair}")
    
    # Show the data in a table
    st.write(historical_data)
    
    # Optional: Plotting the closing prices
    st.line_chart(historical_data.set_index('Timestamp')['Close'])

if __name__ == "__main__":
    main()
