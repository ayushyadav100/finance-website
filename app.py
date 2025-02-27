import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from forex_python.converter import CurrencyRates
from newsapi import NewsApiClient
import requests

# Set page configuration
st.set_page_config(
    page_title="Finance Dashboard",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .main {
        max-width: 1400px;
        padding: 2rem;
    }
    .st-bq {
        border-radius: 15px;
    }
    .stButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Navigation in sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Currency Converter", "Financial News", "Calculators"])

# Stock Market Dashboard
def dashboard():
    st.title("📈 Stock Market Dashboard")
    
    # Input for stock symbol and date range
    col1, col2, col3 = st.columns(3)
    with col1:
        symbol = st.text_input("Enter Stock Symbol (e.g., AAPL)", "AAPL").upper()
    with col2:
        start_date = st.date_input("Start Date", datetime(2020, 1, 1))
    with col3:
        end_date = st.date_input("End Date", datetime.today())
    
    # Validate dates
    if start_date > end_date:
        st.error("Error: Start date cannot be after End date")
        return

    try:
        # Fetch stock data with progress indicator
        with st.spinner('Fetching stock data...'):
            stock_data = yf.download(
                symbol,
                start=start_date,
                end=end_date + pd.DateOffset(1),  # Include end date
                progress=False
            )
        
        if not stock_data.empty:
            # Display metrics
            st.subheader(f"📊 {symbol} Stock Performance")
            
            # Calculate metrics
            latest_close = stock_data['Close'][-1]
            ma_50 = stock_data['Close'].rolling(50).mean().iloc[-1]
            ma_200 = stock_data['Close'].rolling(200).mean().iloc[-1]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Price", f"${latest_close:.2f}")
            with col2:
                st.metric("50-Day MA", f"${ma_50:.2f}", 
                          delta=f"{(latest_close - ma_50)/ma_50:.2%}")
            with col3:
                st.metric("200-Day MA", f"${ma_200:.2f}", 
                          delta=f"{(latest_close - ma_200)/ma_200:.2%}")
            
            # Display chart with moving averages
            st.subheader("Price History")
            chart_data = pd.DataFrame({
                'Close': stock_data['Close'],
                '50-Day MA': stock_data['Close'].rolling(50).mean(),
                '200-Day MA': stock_data['Close'].rolling(200).mean()
            })
            st.line_chart(chart_data)
            
            # Display data table
            st.subheader("Historical Data")
            st.dataframe(stock_data.tail(10).style.format({
                'Open': '{:.2f}',
                'High': '{:.2f}',
                'Low': '{:.2f}',
                'Close': '{:.2f}',
                'Adj Close': '{:.2f}',
                'Volume': '{:,}'
            }))
            
        else:
            st.warning("No data found for the given stock symbol and date range")
            
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        st.markdown("""
        **Common Solutions:**
        1. Check if the stock symbol is valid
        2. Verify date range contains valid trading days
        3. Try a shorter date range
        4. Check your internet connection
        """)

# Currency Converter
def currency_converter():
    st.title("💱 Currency Converter")
    
    # Get available currencies from Yahoo Finance
    try:
        fx_pairs = ['USDJPY=X', 'EURUSD=X', 'GBPUSD=X', 'AUDUSD=X', 'USDKRW=X']
        currencies = sorted(list(set([pair[:3] for pair in fx_pairs] + [pair[3:6] for pair in fx_pairs])))
    except:
        currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'KRW']

    col1, col2, col3 = st.columns(3)
    with col1:
        from_currency = st.selectbox("From Currency", currencies, index=0)
    with col2:
        to_currency = st.selectbox("To Currency", currencies, index=1)
    with col3:
        amount = st.number_input("Amount", min_value=0.1, value=1.0, step=0.1)

    if st.button("Convert"):
        try:
            # Use Yahoo Finance for conversion rates
            pair = f"{from_currency}{to_currency}=X"
            data = yf.download(pair, period="1d")
            
            if not data.empty:
                rate = data['Close'][-1]
                result = amount * rate
                st.success(f"✅ {amount} {from_currency} = {result:.4f} {to_currency}")
                
                # Display historical data
                st.subheader("Historical Exchange Rates (Last 30 Days)")
                hist_data = yf.download(pair, period="1mo")['Close']
                st.line_chart(hist_data)
            else:
                st.error("Currency pair not found. Please try different currencies.")
                
        except Exception as e:
            st.error(f"Conversion failed: {str(e)}")
            st.info("Common reasons: Invalid currency pair or temporary service unavailability")

# Financial News
def financial_news():
    st.title("📰 Financial News")
    
    # News API integration
    newsapi = NewsApiClient(api_key='96445658b5b8419f9e5dc0df21062998')  # Replace with your NewsAPI key
    
    try:
        news = newsapi.get_top_headlines(category='business', language='en', country='us')
        
        if news['totalResults'] > 0:
            for article in news['articles']:
                with st.expander(article['title']):
                    st.write(f"**Source**: {article['source']['name']}")
                    st.write(f"**Published**: {article['publishedAt'][:10]}")
                    st.write(article['description'])
                    st.markdown(f"[Read more]({article['url']})")
        else:
            st.warning("No financial news found.")
            
    except Exception as e:
        st.error(f"Error fetching news: {str(e)}")

# Financial Calculators
def calculators():
    st.title("🧮 Financial Calculators")
    
    # Compound Interest Calculator
    with st.expander("Compound Interest Calculator"):
        principal = st.number_input("Principal Amount ($)", min_value=0, value=1000)
        rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, value=5.0)
        years = st.number_input("Investment Period (Years)", min_value=1, value=10)
        compound_freq = st.selectbox("Compounding Frequency", 
                                   ["Annually", "Monthly", "Daily"])
        
        freq_map = {"Annually": 1, "Monthly": 12, "Daily": 365}
        n = freq_map[compound_freq]
        
        amount = principal * (1 + (rate/100)/n) ** (n * years)
        st.subheader(f"Future Value: ${amount:,.2f}")

# Page routing
if page == "Dashboard":
    dashboard()
elif page == "Currency Converter":
    currency_converter()
elif page == "Financial News":
    financial_news()
elif page == "Calculators":
    calculators()

# Footer
st.markdown("---")
st.markdown("© 2025 Finance Dashboard - Created with Streamlit")