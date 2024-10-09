import streamlit as st
import pandas as pd
from binance.client import Client

# Set up the page
st.set_page_config(page_title="Getting BREAKOUT Data", page_icon="💰")

# Initialize the Binance client without API key
client = Client("", "")

@st.cache_data
def fetch_binance_pairs():
    try:
        exchange_info = client.get_exchange_info()
        usdt_pairs = [symbol['symbol'] for symbol in exchange_info['symbols'] if symbol['quoteAsset'] == 'USDT']
        return usdt_pairs
    except Exception as e:
        st.error(f"Error fetching trading pairs: {e}")
        return []

@st.cache_data
def fetch_binance_historical_data(symbol):
    try:
        klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, "30 days ago UTC")
        df = pd.DataFrame(klines, columns=["OpenTime", "Open", "High", "Low", "Close", "Volume", 
                                             "CloseTime", "QuoteAssetVolume", "NumberOfTrades", 
                                             "TakerBuyBaseAssetVolume", "TakerBuyQuoteAssetVolume", "Ignore"])
        df['OpenTime'] = pd.to_datetime(df['OpenTime'], unit='ms')
        df['Close'] = pd.to_numeric(df['Close'])
        return df[['OpenTime', 'Open', 'High', 'Low', 'Close', 'Volume']]
    except Exception as e:
        st.error(f"Error fetching historical data for {symbol}: {e}")
        return pd.DataFrame()

def main():
    pairs = fetch_binance_pairs()

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
        st.write(historical_data)
        st.line_chart(historical_data.set_index('OpenTime')['Close'])
    else:
        st.warning("No historical data available for this trading pair.")

if __name__ == "__main__":
    main()




