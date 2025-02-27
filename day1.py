import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import requests
from newsapi import NewsApiClient
import plotly.graph_objects as go

# Add this with other imports
from streamlit import session_state as state

# Initialize session state
if 'conversion_result' not in state:
    state.conversion_result = None

# Set page configuration with better visuals
st.set_page_config(
    page_title="Finance Hub",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling with improved aesthetics
st.markdown("""
<style>
    .main {
        background: #0f172a !important;
        color: #e2e8f0 !important;
    }
    
    .stSelectbox, .stNumberInput, .stTextInput {
        background: #1e293b !important;
        border-radius: 8px;
        padding: 0.5rem;
    }
    
    .st-bq, .stAlert {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
    }
    
    .stButton>button {
        background: #3b82f6 !important;
        color: white !important;
        border: none !important;
    }
    
    /* Fix white flash */
    .stApp > div {
        background: #0f172a;
    }
</style>
""", unsafe_allow_html=True)

# Navigation in sidebar with icons
st.sidebar.title("💰 Financial Suite")
pages = {
    "📈 Market Dashboard": "dashboard",
    "💱 Currency Exchange": "currency",
    "📰 Financial News": "news",
    "🧮 Calculators": "calculators",
    "📊 Portfolio Tracker": "portfolio",
    "🌐 Crypto Watch": "crypto"
}
page = st.sidebar.radio("Navigate", list(pages.keys()))

# Hero Section
def show_hero():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #434343 0%, #000000 100%); 
                padding: 4rem; 
                border-radius: 15px;
                color: white;
                text-align: center;
                margin-bottom: 2rem;">
        <h1 style="color: white; font-size: 3.5rem;">Financial Intelligence Suite</h1>
        <p style="font-size: 1.2rem;">Your Comprehensive Financial Analysis Platform</p>
    </div>
    """, unsafe_allow_html=True)

# Enhanced Stock Market Dashboard
def dashboard():
    show_hero()
    with st.container():
        st.title("📈 Real-Time Market Analytics")
        
        # Stock Search Section
        col1, col2, col3 = st.columns([2,1,1])
        with col1:
            symbol = st.text_input("Enter Stock Symbol (e.g., AAPL)", "AAPL").upper()
        with col2:
            start_date = st.date_input("Start Date", datetime(2020, 1, 1))
        with col3:
            end_date = st.date_input("End Date", datetime.today())
        
        # Fetch and display data
        if st.button("Analyze Stock"):
            with st.spinner('Crunching financial data...'):
                try:
                    stock_data = yf.download(symbol, start=start_date, end=end_date)
                    if not stock_data.empty:
                        # Debug: Display preview of the data
                        st.write("Stock Data Preview:", stock_data.head())
                        
                        # Advanced Metrics
                        st.subheader(f"📊 {symbol} Deep Analysis")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.markdown(
                                '<div class="metric-box">52W High<br>${:.2f}</div>'.format(
                                    float(stock_data['High'].max())
                                ),
                                unsafe_allow_html=True
                            )
                        with col2:
                            st.markdown(
                                '<div class="metric-box">Volatility<br>{:.2%}</div>'.format(
                                    float(stock_data['Close'].pct_change().std())
                                ),
                                unsafe_allow_html=True
                            )
                        with col3:
                            st.markdown(
                                '<div class="metric-box">RSI (14d)<br>{:.2f}</div>'.format(
                                    float(calculate_rsi(stock_data))
                                ),
                                unsafe_allow_html=True
                            )
                        with col4:
                            st.markdown(
                                '<div class="metric-box">Volume Avg<br>{:,.0f}</div>'.format(
                                    float(stock_data['Volume'].mean())
                                ),
                                unsafe_allow_html=True
                            ) 

                        # Interactive Plotly Chart
                        fig = go.Figure()
                        fig.add_trace(go.Candlestick(x=stock_data.index,
                                        open=stock_data['Open'],
                                        high=stock_data['High'],
                                        low=stock_data['Low'],
                                        close=stock_data['Close'],
                                        name='Market Data'))
                        fig.update_layout(height=600, title=f'{symbol} Price Analysis')
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No data found. Please check the symbol and date range.")
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")

# New Portfolio Tracker Feature
def portfolio_tracker():
    show_hero()
    st.title("📊 Smart Portfolio Manager")
    
    # Initialize portfolio in session_state if it doesn't exist
    if "portfolio" not in st.session_state:
        st.session_state["portfolio"] = []
    
    with st.expander("Add New Investment"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            asset_type = st.selectbox("Asset Type", ["Stock", "Crypto", "ETF"])
        with col2:
            symbol = st.text_input("Symbol")
        with col3:
            quantity = st.number_input("Quantity", min_value=0.0, format="%.2f")
        with col4:
            purchase_date = st.date_input("Purchase Date")
        
        if st.button("Add to Portfolio"):
            if symbol.strip() == "" or quantity <= 0:
                st.error("Please enter a valid symbol and quantity.")
            else:
                # Save the new investment as a dictionary
                new_investment = {
                    "Asset Type": asset_type,
                    "Symbol": symbol.upper(),
                    "Quantity": quantity,
                    "Purchase Date": purchase_date.strftime("%Y-%m-%d")
                }
                st.session_state["portfolio"].append(new_investment)
                st.success("Asset added to portfolio!")
    
    st.subheader("Your Portfolio")
    if st.session_state["portfolio"]:
        df_portfolio = pd.DataFrame(st.session_state["portfolio"])
        st.dataframe(df_portfolio)
    else:
        st.info("No investments added yet.")

# New Crypto Market Section
def crypto_watch():
    show_hero()
    st.title("🌐 Cryptocurrency Monitor")
    crypto_list = ["BTC-USD", "ETH-USD", "XRP-USD", "DOGE-USD"]
    
    selected = st.multiselect("Select Cryptocurrencies", crypto_list, default=["BTC-USD"])
    if selected:
        data = yf.download(selected, period="1d")['Close']
        st.subheader("Real-Time Prices")
        cols = st.columns(len(selected))
        for idx, crypto in enumerate(selected):
            price = data[crypto].iloc[-1]
            change = data[crypto].pct_change().iloc[-1] * 100
            cols[idx].metric(crypto.split('-')[0], f"${price:,.2f}", f"{change:.2f}%")

# Currency exchange
def currency_converter():
    st.title("💱 Global Currency Converter")
    
    # Comprehensive list of 60+ currencies (ISO 4217 codes)
    currencies = [
        'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'SEK', 'NZD',
        'MXN', 'SGD', 'HKD', 'NOK', 'KRW', 'TRY', 'INR', 'RUB', 'BRL', 'ZAR',
        'DKK', 'PLN', 'THB', 'IDR', 'HUF', 'CZK', 'ILS', 'CLP', 'PHP', 'AED',
        'COP', 'SAR', 'MYR', 'RON', 'BGN', 'ARS', 'EGP', 'QAR', 'KWD', 'KZT',
        'UAH', 'NGN', 'BDT', 'MAD', 'OMR', 'PKR', 'DZD', 'TWD', 'VND', 'PEN',
        'IRR', 'CRC', 'JOD', 'LKR', 'BHD', 'UYU', 'NPR', 'LYD', 'KES', 'ISK',
        'TND', 'ETB', 'GHS', 'RSD', 'HNL', 'GTQ', 'PYG', 'BOB', 'SVC', 'ALL'
    ]

    col1, col2, col3 = st.columns(3)
    with col1:
        from_currency = st.selectbox("From Currency", currencies, index=0)
    with col2:
        to_currency = st.selectbox("To Currency", currencies, index=1)
    with col3:
        amount = st.number_input("Amount", min_value=0.1, value=1.0, step=0.1)

    if st.button("Convert"):
        try:
            if from_currency == to_currency:
                raise ValueError("Cannot convert identical currencies")
            
            # Try multiple pair formats
            pairs_to_try = [
                f"{from_currency}{to_currency}=X",
                f"{to_currency}{from_currency}=X",
                f"{from_currency}USD=X",  # Use USD as intermediate
                f"USD{to_currency}=X"
            ]
            
            rate = None
            with st.spinner("Checking exchange rates..."):
                for pair in pairs_to_try:
                    try:
                        data = yf.download(pair, period="1d", progress=False)
                        if not data.empty:
                            rate = data['Close'].iloc[-1]
                            if pair.startswith(to_currency) or pair.endswith("USD=X"):
                                rate = 1/rate
                            break
                    except:
                        continue
            
            if rate is None:
                raise ValueError(f"Could not find exchange rate for {from_currency} to {to_currency}")
            
            result = amount * rate
            st.success(f"**{amount:.2f} {from_currency} = {result:.4f} {to_currency}**")
            
            # Show historical data for valid pairs
            with st.spinner("Loading historical trends..."):
                try:
                    hist_data = yf.download(pairs_to_try[0], period="1mo", progress=False)['Close']
                    if not hist_data.empty:
                        st.write("Historical Data Preview:", hist_data.head())
                        st.subheader("30-Day Exchange Rate History")
                        st.line_chart(hist_data)
                    else:
                        st.warning("Historical data unavailable for this pair")
                except Exception as hist_error:
                    st.error(f"Historical data error: {str(hist_error)}")

        except Exception as e:
            st.error(str(e))
            st.markdown("""
            **Troubleshooting Tips:**
            1. Try converting through USD (e.g. Local → USD → Target)
            2. Check currency codes are 3-letter ISO format
            3. Some exotic currencies may have limited availability
            """)

# Financial news 
def financial_news():
    st.title("📰 Financial News")
    st.image("https://fichindu.in/wp-content/uploads/2024/10/image-1.png",
             width=100,
             use_column_width=False,
             caption="Latest Market News")
    
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

# Enhanced Calculators
def financial_calculators():
    show_hero()
    st.title("🧮 Financial Tools Hub")
    
    with st.expander("Advanced Compound Calculator", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            principal = st.number_input("Principal Amount ($)", min_value=0, value=10000)
        with c2:
            years = st.slider("Investment Period (Years)", 1, 50, 10)
        with c3:
            rate = st.slider("Annual Return (%)", 0.0, 20.0, 7.0)
        
        freq = st.selectbox("Compounding Frequency", ["Monthly", "Quarterly", "Annually"])
        n = 12 if freq == "Monthly" else 4 if freq == "Quarterly" else 1
        amount = principal * (1 + (rate/100)/n) ** (n * years)
        
        st.subheader(f"Future Value: ${amount:,.2f}")
        st.markdown(
            f"<div style='background: #e3f2fd !important; padding: 1rem; border-radius: 10px; border: 2px solid #6B8DD6;'>"
            f"Growth Visualization: {principal:,.0f} → {amount:,.0f} "
            f"({amount/principal:.1f}x growth)</div>",
            unsafe_allow_html=True
        )

    with st.expander("Loan EMI Calculator"):
        # Add loan calculator logic
        pass

# Helper function for technical indicators
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs)).iloc[-1]

# Page routing
if pages[page] == "dashboard":
    dashboard()
elif pages[page] == "currency":
    currency_converter()
elif pages[page] == "news":
    financial_news()
elif pages[page] == "calculators":
    financial_calculators()
elif pages[page] == "portfolio":
    portfolio_tracker()
elif pages[page] == "crypto":
    crypto_watch()

# Footer with social links
st.markdown("---")
footer = """
<div style="text-align: center; padding: 2rem; color: #666;">
    <div style="margin-bottom: 1rem;">
        <a href="#" style="margin: 0 1rem; color: #666; text-decoration: none;">📚 Tutorial</a>
        <a href="#" style="margin: 0 1rem; color: #666; text-decoration: none;">📈 Market Data</a>
        <a href="#" style="margin: 0 1rem; color: #666; text-decoration: none;">📧 Contact</a>
    </div>
    <div>© 2025 Financial Suite | 📊 Data Sources: Yahoo Finance, NewsAPI</div>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)
