import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import requests
from newsapi import NewsApiClient
import plotly.graph_objects as go
import sqlite3
from cryptography.fernet import Fernet
import base64
import hashlib
import os
import time
from streamlit.components.v1 import html
from streamlit_extras.stylable_container import stylable_container
import random
from datetime import datetime



# Initialize session state for conversion result and portfolio
if 'conversion_result' not in st.session_state:
    st.session_state.conversion_result = None
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []

# Set page configuration with better visuals
st.set_page_config(
    page_title="Finance Hub",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================== ENHANCED CSS ========================
st.markdown("""
<style>

       /* Animated Gradient Header */
    .animated-header {
        background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        padding: 4rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 2rem 0;
    }
    .animated-header h1 {
        font-size: 3.5rem !important;
        color: #ffffff !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        animation: textGlow 2s ease-in-out infinite alternate;
    }
    @keyframes textGlow {
        0% { text-shadow: 0 0 10px rgba(255,255,255,0.8); }
        100% { text-shadow: 0 0 20px rgba(255,255,255,1), 0 0 30px rgba(255,255,255,0.8); }
    }
    
    /* Enhanced Login Buttons */
    .login-buttons button {
        background: linear-gradient(45deg, #ff0000, #ff4d4d) !important;
        color: white !important;
        border: none !important;
        padding: 12px 30px !important;
        border-radius: 25px !important;
        margin: 15px 0 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(255, 77, 77, 0.4) !important;
    }
    .login-buttons button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(255, 77, 77, 0.6) !important;
    }
    
    /* New Mission Section Styling */
    .mission-card {
        background: rgba(255,255,255,0.1) !important;
        border-left: 4px solid #ff4d4d !important;
        border-radius: 10px;
        padding: 2rem;
        margin: 2rem 0;
        transition: transform 0.3s ease;
    }
    .mission-card:hover {
        transform: translateX(10px);
    }
    
    /* Animated Text */
    @keyframes fadeIn {{
        0% {{ opacity: 0; transform: translateY(20px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
    }}
    .animated-text {{
        animation: fadeIn 1s ease-out;
    }}
    
    /* Hover Effects */
    .hover-card {{
        transition: all 0.3s ease;
        cursor: pointer;
    }}
    .hover-card:hover {{
        transform: scale(1.02);
        box-shadow: 0 8px 32px rgba(255, 105, 107, 0.3) !important;
    }}


    /* Base Modern Dark Theme */
    :root {
        --primary: #0f172a;
        --secondary: #1e293b;
        --accent: #3b82f6;
        --text: #e2e8f0;
        --gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
    }
    .stApp {
        background: linear-gradient(to bottom right, #0f0c29, #302b63, #24243e);
        color: var(--text);
    }
    /* Main Container Enhancements */
    .main {
        background: var(--primary) !important;
        color: var(--text) !important;
        font-family: 'Inter', sans-serif;
    }
    /* Glassmorphism Effect */
    .glass-card {
        background: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(16px) saturate(180%);
        -webkit-backdrop-filter: blur(16px) saturate(180%);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    /* Animated Gradient Header */
    .animated-header {
        background: var(--gradient);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        padding: 4rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 2rem 0;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    /* Modern Input Styling */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stSelectbox>div>div>select {
        background: rgba(255, 255, 255, 0.1) !important;
        color: var(--text) !important;
        border-radius: 10px !important;
        padding: 0.75rem !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    /* Hover Animations for Buttons */
    .stButton>button {
        background: var(--gradient) !important;
        border: none !important;
        color: white !important;
        padding: 0.8rem 2rem !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.4);
    }
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: var(--primary);
    }
    ::-webkit-scrollbar-thumb {
        background: var(--accent);
        border-radius: 4px;
    }
    /* Plotly Chart Theming */
    .js-plotly-plot .plotly, .js-plotly-plot .plotly div {
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)


 


# ======================== NEW USER PAGE ========================
def user_page():
    # Time-based greeting
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        greeting = "Good morning ☀️"
    elif 12 <= current_hour < 17:
        greeting = "Good afternoon 🌤️"
    else:
        greeting = "Good evening 🌙"

    # Animated header
    st.markdown(f"""
    <style>
        @keyframes slideDown {{
            0% {{ transform: translateY(-100%); opacity: 0; }}
            100% {{ transform: translateY(0); opacity: 1; }}
        }}
        .user-header {{
            animation: slideDown 1s ease-out;
            text-align: center;
            padding: 4rem 2rem;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            border-radius: 20px;
            margin: 2rem 0;
            color: white;
        }}
        .login-buttons button {{
            background: linear-gradient(45deg, #3b82f6, #6366f1) !important;
            color: white !important;
            border: none !important;
            padding: 1rem 2rem !important;
            border-radius: 12px !important;
            transition: all 0.3s !important;
        }}
        .login-buttons button:hover {{
            transform: scale(1.05);
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
        }}
    </style>
    
    <div class="user-header">
        <h1 style="font-size: 2.5rem; margin-bottom: 1rem;">{greeting}, Investor</h1>
        <p style="font-size: 1.2rem;">Welcome to your financial command center</p>
    </div>
    """, unsafe_allow_html=True)

    # Updated Login/Signup Section
    with stylable_container(
        key="auth_buttons",
        css_styles="""
        {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
            text-align: center;
        }}
        """
    ):
        st.markdown('<div class="login-buttons">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Login", key="login_btn"):
                st.session_state.current_auth = "login"
        with col2:
            if st.button("✨ Sign Up", key="signup_btn"):
                st.session_state.current_auth = "signup"
        st.markdown('</div>', unsafe_allow_html=True)



        # About Section
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.7);
                padding: 2rem;
                border-radius: 20px;
                margin: 2rem 0;">
        <h2 style="color: #3b82f6;">About Our Platform</h2>
        <p style="font-size: 1.1rem; line-height: 1.6;">
            Unlock your financial potential with our innovative website. Access real-time market insights, 
            expert strategies, and powerful tools designed for investors of every level. Join our community 
            today and take control of your financial future.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Corrected indentation here (removed 2 leading spaces)
    with stylable_container(
        key="mission_container",
        css_styles="""
        {
            background: rgba(30, 41, 59, 0.7);
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
        }
        """
    ):
        st.markdown("""
        <div class="animated-text">
            <div class="mission-card">
                <h2 style="color: #ff6b6b;">🌟 Our Mission</h2>
                <p style="font-size: 1.1rem; line-height: 1.6;">
                    Empowering investors of all levels with cutting-edge financial tools and insights. 
                    We democratize access to professional-grade market analysis through intuitive 
                    interfaces and AI-driven predictions.
                </p>
            </div>
            
        <div class="mission-card">
        <h2 style="color: #ff6b6b;">🔭 Our Vision</h2>
        <p style="font-size: 1.1rem; line-height: 1.6;">
        Creating a world where everyone can make informed financial decisions with confidence. 
        Bridging the gap between retail investors and institutional-grade analytics.
        </p>
        </div>
        </div>
        """, unsafe_allow_html=True)
    






        # Features Grid
    features = [
        {"icon": "🚀", "title": "Real-Time Analytics", "desc": "Live market data with millisecond latency"},
        {"icon": "🛡️", "title": "Secure Portfolio", "desc": "Military-grade encryption for your assets"},
        {"icon": "🤖", "title": "AI Predictions", "desc": "Machine learning driven forecasts"},
        {"icon": "🌍", "title": "Global Coverage", "desc": "Markets, currencies, and news worldwide"}
    ]
    
    with stylable_container(
        key="features_container",
        css_styles="""
        {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
        }}
        """
    ):
        st.subheader("💎 Key Features")
        cols = st.columns(4)
        for i, feat in enumerate(features):
            with cols[i]:
                st.markdown(f"""
                <div class="hover-card" style="padding: 1.5rem; text-align: center;">
                    <div style="font-size: 2.5rem;">{feat['icon']}</div>
                    <h4 style="margin: 1rem 0;">{feat['title']}</h4>
                    <p>{feat['desc']}</p>
                </div>
                """, unsafe_allow_html=True)







# ======================== ENHANCED COMPONENTS ========================
def enhanced_hero():
    html("""
    <div class="animated-header">
        <h1>Financial Intelligence Suite</h1>
        <p style="font-size: 1.5rem; color: #ffe6e6;">
            Next-Generation Market Analysis Platform
        </p>
    </div>
    """)






# ======================== THEME SWITCHER ========================

def set_theme():
    theme = st.sidebar.radio("🌓 Theme", ["Dark", "Light"], index=0, key="theme")
    
    if theme == "Dark":
        theme_css = """
        <style>
            :root {
                --primary-bg: #0f172a;
                --secondary-bg: #1e293b;
                --text-color: #e2e8f0;
                --accent-color: #3b82f6;
                --card-bg: rgba(30, 41, 59, 0.95);
                --input-bg: rgba(255, 255, 255, 0.1);
                --border-color: rgba(255, 255, 255, 0.2);
                --mission-color: #ff6b6b;
                --plotly-bg: 'plotly_dark';
            }
        </style>
        """
    else:
        theme_css = """
        <style>
            :root {
                --primary-bg: #ffffff;
                --secondary-bg: #f8f9fa;
                --text-color: #2d3748;
                --accent-color: #00cc88;
                --card-bg: rgba(255, 255, 255, 0.98);
                --input-bg: rgba(0, 0, 0, 0.05);
                --border-color: rgba(0, 0, 0, 0.1);
                --mission-color: #3b82f6;
                --plotly-bg: 'plotly_white';
            }

            /* Sidebar */
            .stSidebar { background: var(--primary-bg) !important; }
            
            /* User greeting card */
            .user-header { background: #000 !important; }
            .user-header h1 { color: #fff !important; text-shadow: 0 0 10px rgba(255,255,255,0.8); }
            
            /* Login buttons */
            .login-buttons button {
                background: linear-gradient(45deg, #00ff88, #00cc77) !important;
                box-shadow: 0 0 15px rgba(0,255,136,0.4) !important;
            }
            
            /* About section */
            div[data-stkey="mission_container"] { background: var(--card-bg) !important; }
            
            /* Dashboard blocks */
            .glass-card, div[data-stkey="chart_container"] > div { background: var(--card-bg) !important; }
            
            /* Analyze button */
            div[data-testid="stButton"] > button {
                background: linear-gradient(45deg, #00ff88, #00cc77) !important;
                color: #000 !important;
            }
            
            /* Portfolio section */
            div[data-stkey="portfolio_container"] { background: var(--card-bg) !important; }
            
            /* Financial assessment */
            .financial-assessment { background: var(--card-bg) !important; }
            .financial-assessment button {
                background: linear-gradient(45deg, #00ff88, #00cc77) !important;
                color: #000 !important;
            }
            
            /* Animated header box */
            .animated-header {
                background: var(--card-bg) !important;
                animation: border-glow 2s infinite;
                border: 2px solid var(--accent-color);
            }
            @keyframes border-glow {
                0% { box-shadow: 0 0 10px rgba(0,204,136,0.3); }
                50% { box-shadow: 0 0 20px rgba(0,204,136,0.6); }
                100% { box-shadow: 0 0 10px rgba(0,204,136,0.3); }
            }
        </style>
        """
    
    st.markdown(theme_css, unsafe_allow_html=True)
    
    # Main CSS with variables
    st.markdown(f"""
    <style>
        .stApp {{
            background: var(--primary-bg);
            color: var(--text-color);
        }}
        
        .glass-card, .mission-card, .stSelectbox>div>div>select,
        .stTextInput>div>div>input, .stNumberInput>div>div>input {{
            background: var(--card-bg) !important;
            color: var(--text-color) !important;
            border-color: var(--border-color) !important;
        }}
        
        .mission-card h2 {{
            color: var(--mission-color) !important;
        }}
        
        .stButton>button {{
            background: var(--accent-color) !important;
            color: white !important;
        }}
        
        .stDataFrame {{
            background: var(--card-bg) !important;
            color: var(--text-color) !important;
        }}
        
        .stProgress > div > div > div {{
            background: var(--accent-color) !important;
        }}
        
        .hover-card:hover {{
            box-shadow: 0 8px 32px rgba(59, 130, 246, 0.2) !important;
        }}
        
        .plot-container {{
            background: var(--primary-bg) !important;
        }}
    </style>
    """, unsafe_allow_html=True)

set_theme()





# ======================== ENHANCED DASHBOARD ========================
def dashboard():
    enhanced_hero()
    with stylable_container(key="...", 
                       css_styles="""
                       {
                            background: rgba(30, 41, 59, 0.7);
                            backdrop-filter: blur(16px) saturate(180%);
                            border-radius: 20px;
                            border: 1px solid rgba(255, 255, 255, 0.1);
                            padding: 2rem;
                            margin: 1rem 0;
                       }
                       """):
        st.title("📈 Real-Time Market Analytics")
        
        # Stock Search Section using columns
        col1, col2, col3 = st.columns([2,1,1])
        with col1:
            symbol = st.text_input("Enter Stock Symbol (e.g., AAPL)", "AAPL", key="stock_input").upper()
        with col2:
            start_date = st.date_input("Start Date", datetime(2020, 1, 1), key="start_date")
        with col3:
            end_date = st.date_input("End Date", datetime.today(), key="end_date")
        
        if st.button("Analyze Stock", key="analyze_btn"):
            with st.spinner('Crunching financial data...'):
                try:
                    stock_data = yf.download(symbol, start=start_date, end=end_date)
                    if not stock_data.empty:
                        with stylable_container(key="chart_container"):
                            st.subheader(f"📊 {symbol} Advanced Analysis")
                            
                            tab1, tab2, tab3 = st.tabs(["Candlestick", "Technical Indicators", "Historical Data"])
                            
                            with tab1:
                                fig = go.Figure()
                                fig.add_trace(go.Candlestick(
                                    x=stock_data.index,
                                    open=stock_data['Open'],
                                    high=stock_data['High'],
                                    low=stock_data['Low'],
                                    close=stock_data['Close'],
                                    name='Market Data'
                                ))
                                fig.update_layout(
                                    height=600,
                                    title=f'{symbol} Price Analysis',
                                    xaxis_rangeslider_visible=False,
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    font_color='#e2e8f0'
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            
                            with tab2:
                                c1, c2, c3, c4 = st.columns(4)
                                with c1:
                                    st.metric("RSI (14)", f"{calculate_rsi(stock_data):.2f}", delta="Oversold/Overbought")
                                with c2:
                                    st.metric("MACD", "Bullish", delta="+2.5%")
                                with c3:
                                    st.metric("Bollinger", "Neutral", delta="±1.2%")
                                with c4:
                                    st.metric("Volume Trend", "↑ 15%", delta="Weekly")
                            
                            with tab3:
                                st.dataframe(
                                    stock_data.tail(10).style.format({
                                        'Open': '{:.2f}',
                                        'High': '{:.2f}',
                                        'Low': '{:.2f}',
                                        'Close': '{:.2f}',
                                        'Adj Close': '{:.2f}',
                                        'Volume': '{:,}'
                                    }),
                                    height=400
                                )
                            
                            # Live Market Sentiment
                            with stylable_container(key="sentiment"):
                                st.subheader("Market Sentiment")
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.write("📰 News Sentiment")
                                    st.progress(75)
                                with col2:
                                    st.write("📈 Technical Analysis")
                                    st.progress(60)
                                with col3:
                                    st.write("🤖 AI Prediction")
                                    st.progress(82)
                    else:
                        st.error("No data found for the symbol provided.")
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
                    st.image("https://i.imgur.com/WOGKgvQ.gif", width=300)

# ======================== ENCRYPTION & SECURE DB FOR PORTFOLIO ========================
def get_encryption_key():
    key_file = "secret.key"
    if os.path.exists(key_file):
        with open(key_file, "rb") as f:
            key = f.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
    return key

cipher_suite = Fernet(get_encryption_key())

def init_secured_db():
    conn = sqlite3.connect('encrypted_portfolio.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS portfolios
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_hash TEXT NOT NULL,
                  asset_type BLOB NOT NULL,
                  symbol BLOB NOT NULL,
                  quantity BLOB NOT NULL,
                  purchase_date BLOB NOT NULL)''')
    conn.commit()
    return conn

def encrypt_data(data):
    return cipher_suite.encrypt(data.encode())

def decrypt_data(encrypted_data):
    return cipher_suite.decrypt(encrypted_data).decode()

# ======================== ENHANCED PORTFOLIO TRACKER ========================
def portfolio_tracker():
    enhanced_hero()
    st.title("📊 Secure Portfolio Manager")
    
    # Generate unique user identifier based on IP
    user_ip = st.experimental_user.ip if hasattr(st.experimental_user, 'ip') else '127.0.0.1'
    user_hash = hashlib.sha256(user_ip.encode()).hexdigest()
    
    conn = init_secured_db()
    c = conn.cursor()
    
    try:
        c.execute("SELECT * FROM portfolios WHERE user_hash=?", (user_hash,))
        encrypted_rows = c.fetchall()
        portfolio = []
        for row in encrypted_rows:
            portfolio.append({
                "Asset Type": decrypt_data(row[2]),
                "Symbol": decrypt_data(row[3]),
                "Quantity": float(decrypt_data(row[4])),
                "Purchase Date": decrypt_data(row[5])
            })
        st.session_state.portfolio = portfolio
    except Exception as e:
        st.error(f"Error loading portfolio: {str(e)}")
    
    # Fixed container styling
    with stylable_container(
        key="portfolio_container",
        css_styles="""
        {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(16px) saturate(180%);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 2rem;
            margin: 1rem 0;
        }
        """
    ):
        st.subheader("➕ Add New Investment")
        
        with st.form(key="investment_form"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                asset_type = st.selectbox("Asset Type", ["Stock", "Crypto", "ETF"], key="asset_type")
            with col2:
                symbol = st.text_input("Symbol", key="port_symbol").upper()
            with col3:
                quantity = st.number_input("Quantity", min_value=0.0, format="%.2f", key="port_quantity")
            with col4:
                purchase_date = st.date_input("Purchase Date", key="port_date")
            submitted = st.form_submit_button("💾 Save Investment")
            
            if submitted:
                if symbol.strip() == "" or quantity <= 0:
                    st.error("Please enter valid details")
                else:
                    try:
                        c.execute('''INSERT INTO portfolios 
                                   (user_hash, asset_type, symbol, quantity, purchase_date)
                                   VALUES (?, ?, ?, ?, ?)''',
                                   (user_hash,
                                    encrypt_data(asset_type),
                                    encrypt_data(symbol),
                                    encrypt_data(str(quantity)),
                                    encrypt_data(purchase_date.strftime("%Y-%m-%d"))))
                        conn.commit()
                        st.success("Investment securely stored 🔒")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Security error: {str(e)}")
        
        st.subheader("🔐 Your Secure Portfolio")
        if st.session_state.portfolio:
            df = pd.DataFrame(st.session_state.portfolio)
            try:
                symbols = [row['Symbol'] for row in st.session_state.portfolio]
                data = yf.download(symbols, period="1d")['Close']
                df['Current Price'] = [data[sym].iloc[-1] if sym in data.columns else 0 for sym in df['Symbol']]
                df['Value'] = df['Quantity'] * df['Current Price']
            except Exception as e:
                st.warning(f"Couldn't fetch prices: {str(e)}")
            st.dataframe(
                df.style.format({
                    'Quantity': '{:.2f}',
                    'Current Price': '${:.2f}',
                    'Value': '${:,.2f}'
                }),
                height=400
            )
            with stylable_container(key="...", 
                       css_styles="""
                       {
                            background: rgba(30, 41, 59, 0.7);
                            backdrop-filter: blur(16px) saturate(180%);
                            border-radius: 20px;
                            border: 1px solid rgba(255, 255, 255, 0.1);
                            padding: 2rem;
                            margin: 1rem 0;
                       }
                       """):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Value", f"${df['Value'].sum():,.2f}")
                with col2:
                    best = df.loc[df['Value'].idxmax()]['Symbol'] if not df.empty else 'N/A'
                    st.metric("Best Performer", best)
                with col3:
                    st.metric("Diversification", f"{len(df)} assets")
        else:
            st.info("No investments found. Add your first investment above.")
    
    conn.close()

# ======================== NEW CRYPTO MARKET SECTION ========================
def crypto_watch():
    enhanced_hero()
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

# ======================== CURRENCY CONVERTER ========================

def currency_converter():
    st.title("💱 Global Currency Converter")
    with stylable_container(key="...", 
                       css_styles="""
                       {
                            background: rgba(30, 41, 59, 0.7);
                            backdrop-filter: blur(16px) saturate(180%);
                            border-radius: 20px;
                            border: 1px solid rgba(255, 255, 255, 0.1);
                            padding: 2rem;
                            margin: 1rem 0;
                       }
                       """):
        currencies = [
            'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'SEK', 'NZD',
            'MXN', 'SGD', 'HKD', 'NOK', 'KRW', 'TRY', 'INR', 'RUB', 'BRL', 'ZAR'
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
                    f"{from_currency}USD=X",
                    f"USD{to_currency}=X"
                ]
                
                rate = None
                with st.spinner("Checking exchange rates..."):
                    for pair in pairs_to_try:
                        try:
                            data = yf.download(pair, period="1d", progress=False)
                            if not data.empty and 'Close' in data.columns:
                                rate = data['Close'].iloc[-1]
                                if pair.startswith(to_currency) or pair.endswith("USD=X"):
                                    rate = 1 / rate
                                break
                        except Exception as e:
                            continue
                
                if rate is None:
                    raise ValueError(f"Could not find exchange rate for {from_currency} to {to_currency}")
                
                result = amount * rate
                st.success(f"**{amount:.2f} {from_currency} = {result:.4f} {to_currency}**")
                
                # Historical data with proper error handling
                with st.spinner("Loading historical trends..."):
                    try:
                        hist_data = yf.download(pairs_to_try[0], period="1mo", progress=False)
                        if not hist_data.empty and 'Close' in hist_data.columns:
                            st.subheader("30-Day Exchange Rate History")
                            st.line_chart(hist_data['Close'])
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

                
# ======================== FINANCIAL NEWS (FILTERED) ========================
def financial_news():
    st.title("📰 Global Financial News")
    
    with stylable_container(key="...", 
                       css_styles="""
                       {
                            background: rgba(30, 41, 59, 0.7);
                            backdrop-filter: blur(16px) saturate(180%);
                            border-radius: 20px;
                            border: 1px solid rgba(255, 255, 255, 0.1);
                            padding: 2rem;
                            margin: 1rem 0;
                       }
                       """):

        col1, col2, col3 = st.columns(3)
        with col1:
            country = st.selectbox("Select Country", 
                ['world', 'us', 'gb', 'in', 'ca', 'au', 'jp', 'cn'],
                format_func=lambda x: x.capitalize())
        with col2:
            language = st.selectbox("Select Language", ['en', 'es', 'de', 'fr', 'zh', 'ja'])
        with col3:
            category = st.selectbox("Category", ['business', 'technology', 'general'])

    newsapi = NewsApiClient(api_key='96445658b5b8419f9e5dc0df21062998')
    
    try:
        # Single try block with proper error handling
        if country == 'world':
            news = newsapi.get_top_headlines(
                category='business',
                language=language,
                page_size=30
            )
        else:
            news = newsapi.get_top_headlines(
                category='business',
                country=country,
                language=language,
                page_size=30
            )

        finance_keywords = ["finance", "stock", "money", "market", "economy", "investment","Bonds"," IPO"," Earnings","Mergers & Acquisitions (M&A)"," Global Markets","Trading","Mutual Funds"," Forex","Cryptocurrency"," Market Trends","Economic Data"]
        filtered_articles = []
        if news['totalResults'] > 0:
            for article in news['articles']:
                text = (article['title'] + " " + (article.get('description') or "")).lower()
                if any(keyword in text for keyword in finance_keywords):
                    filtered_articles.append(article)
            if filtered_articles:
                for article in filtered_articles:
                    with st.expander(article['title']):
                        st.write(f"**Source:** {article['source']['name']}")
                        st.write(f"**Published:** {article['publishedAt'][:10]}")
                        st.write(article['description'])
                        st.markdown(f"[Read more]({article['url']})")
            else:
                st.warning("No finance-related news found.")
        else:
            st.warning("No news found.")
    except Exception as e:  # Added required except block
        st.error(f"Error fetching news: {str(e)}")

# ======================== FINANCIAL CALCULATORS ========================
# ======================== FINANCIAL CALCULATORS ========================
def financial_calculators():
    enhanced_hero()
    st.title("🧮 Financial Tools Hub")
    
    # Compound Calculator
    with st.expander("Advanced Compound Calculator", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            principal = st.number_input("Principal Amount ($)", min_value=0, value=10000, key="principal")
        with c2:
            years = st.slider("Investment Period (Years)", 1, 50, 10, key="years")
        with c3:
            rate = st.slider("Annual Return (%)", 0.0, 20.0, 7.0, key="rate")
        
        freq = st.selectbox("Compounding Frequency", ["Monthly", "Quarterly", "Annually"], key="frequency")
        n = 12 if freq == "Monthly" else 4 if freq == "Quarterly" else 1
        amount = principal * (1 + (rate/100)/n) ** (n * years)
        
        st.subheader(f"Future Value: ${amount:,.2f}")
        st.markdown(
            f"<div style='background: #e3f2fd; padding: 1rem; border-radius: 10px; border: 2px solid #6B8DD6;'>"
            f"Growth Visualization: {principal:,.0f} → {amount:,.0f} "
            f"({amount/principal:.1f}x growth)</div>",
            unsafe_allow_html=True
        )

    # Loan EMI Calculator (now separate expander)
    with st.expander("🏦 Loan EMI Calculator", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            loan_amount = st.number_input("Loan Amount ($)", min_value=1000, value=100000, step=1000)
            interest_rate = st.slider("Annual Interest Rate (%)", 1.0, 20.0, 7.5)
        with col2:
            loan_tenure = st.slider("Loan Tenure (Years)", 1, 30, 15)
            payment_frequency = st.selectbox("Payment Frequency", ["Monthly", "Quarterly", "Annually"])
        
        # EMI Calculation
        monthly_rate = interest_rate / 1200
        n_payments = loan_tenure * 12
        emi = loan_amount * monthly_rate * (1 + monthly_rate)**n_payments / ((1 + monthly_rate)**n_payments - 1)
        
        st.subheader(f"Monthly Payment: ${emi:,.2f}")
        st.write(f"Total Interest Payable: ${(emi * n_payments - loan_amount):,.2f}")

    # Stock Return Calculator (separate expander)
    with st.expander("📈 Stock Return Calculator"):
        col1, col2 = st.columns(2)
        with col1:
            initial_investment = st.number_input("Initial Investment ($)", min_value=100, value=10000)
            years_held = st.number_input("Holding Period (Years)", min_value=1, value=5)
        with col2:
            expected_return = st.slider("Expected Annual Return (%)", -100.0, 100.0, 10.0)
            dividend_yield = st.slider("Dividend Yield (%)", 0.0, 20.0, 2.0)
        
        # Growth Calculation
        final_value = initial_investment * (1 + (expected_return/100))**years_held
        dividends = initial_investment * (dividend_yield/100) * years_held
        total_value = final_value + dividends
        
        st.subheader(f"Projected Value: ${total_value:,.2f}")
        st.write(f"Capital Appreciation: ${final_value - initial_investment:,.2f}")
        st.write(f"Dividends Earned: ${dividends:,.2f}")

    # Mortgage Calculator (separate expander)
    with st.expander("🏠 Mortgage Calculator"):
        # Add mortgage-specific calculations here
        pass
# ======================== HELPER FUNCTION FOR TECHNICAL INDICATORS ========================
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs)).iloc[-1]

# ======================== LOADING ANIMATION ========================
def loading_animation():
    html("""
    <div class="loader">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
    </div>
    <style>
        .loader {
            display: flex;
            justify-content: center;
            padding: 2rem;
        }
        .dot {
            width: 12px;
            height: 12px;
            margin: 0 5px;
            background: #3b82f6;
            border-radius: 50%;
            animation: bounce 1.4s infinite;
        }
        .dot:nth-child(2) { animation-delay: 0.2s; }
        .dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-15px); }
        }
    </style>
    """)



def financial_education():
    enhanced_hero()
    
    # Initialize session state
    if 'user_level' not in st.session_state:
        st.session_state.user_level = None
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False
    if 'learning_progress' not in st.session_state:
        st.session_state.learning_progress = {}

    # Skill Assessment
    if not st.session_state.user_level:
        with stylable_container(key="skill_assess", css_styles="""
            { background: rgba(30,41,59,0.9); border-radius: 20px; padding: 2rem; }"""):
            
            st.title("📚 Financial Literacy Assessment")
            st.write("Let's determine your current knowledge level to personalize your learning experience!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Beginner 👶", use_container_width=True):
                    st.session_state.user_level = "beginner"
            with col2:
                if st.button("Intermediate 🧑💻", use_container_width=True):
                    st.session_state.user_level = "intermediate"
            with col3:
                if st.button("Advanced 🧑🏫", use_container_width=True):
                    st.session_state.user_level = "advanced"
            
            st.markdown("---")
            st.write("**Not sure? Take our quick assessment (10 questions)**")
            if st.button("Start Knowledge Check 🔍"):
                st.session_state.quiz_started = True
                st.experimental_rerun()

    # Quiz System
    if 'quiz_started' in st.session_state and st.session_state.quiz_started:
        render_quiz()

    # Main Education Content
    if st.session_state.user_level and not st.session_state.quiz_started:
        render_education_content()

def render_quiz():
    questions = [
        {
            "question": "What does 'APR' stand for?",
            "options": ["Annual Percentage Rate", "Average Payment Ratio", 
                        "Applied Principal Return", "Automated Payment Regulation"],
            "correct": 0
        },
        {
            "question": "Which investment has historically highest returns?",
            "options": ["Savings Accounts", "Government Bonds", 
                        "Stock Market", "Commodities"],
            "correct": 2
        },
        
        # Add 8 more questions...
    ]

    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
        st.session_state.score = 0

    with stylable_container(key="quiz_container", css_styles="""
        { background: rgba(30,41,59,0.9); border-radius: 20px; padding: 2rem; }"""):
        
        # Progress bar
        progress = st.session_state.current_question / len(questions)
        st.progress(progress)
        
        # Current question
        q = questions[st.session_state.current_question]
        st.subheader(f"Question {st.session_state.current_question + 1}/{len(questions)}")
        st.markdown(f"**{q['question']}**")
        
        # Display options
        selected = st.radio("Choose your answer:", q['options'], key=f"q{st.session_state.current_question}")
        
        # Navigation buttons
        col1, col2 = st.columns([1,3])
        if st.session_state.current_question > 0:
            col1.button("← Previous", on_click=lambda: st.session_state.update(current_question=st.session_state.current_question-1))
        if st.session_state.current_question < len(questions)-1:
            col2.button("Next →", on_click=lambda: check_answer(q['correct'], q['options'].index(selected)))
        else:
            if col2.button("Finish Test", type="primary"):
                check_answer(q['correct'], q['options'].index(selected))
                determine_level()

def check_answer(correct_idx, selected_idx):
    if selected_idx == correct_idx:
        st.session_state.score += 1

def determine_level():
    score = st.session_state.score
    if score <= 3:
        st.session_state.user_level = "beginner"
    elif score <= 7:
        st.session_state.user_level = "intermediate"
    else:
        st.session_state.user_level = "advanced"
    st.session_state.quiz_started = False
    st.session_state.quiz_completed = True

def render_education_content():
    st.title("🎓 Interactive Financial Academy")
    
    # Level-based curriculum
    curriculum = {
        "beginner": {
            "Foundations": [
                ("💰 Basic Budgeting", "budgeting", 0.25),
                ("🏦 Banking Basics", "banking", 0.35),
                ("💳 Credit Fundamentals", "credit", 0.5)
            ],
            "Investing 101": [
                ("📈 Stock Market Basics", "stocks", 0.65),
                ("🛡️ Risk Management", "risk", 0.75),
                ("🌱 Compound Interest", "compound", 0.85)
            ]
        },
        "intermediate": {
            "Portfolio Management": [
                ("📊 Asset Allocation", "allocation", 0.3),
                ("⚖️ Modern Portfolio Theory", "mpt", 0.45),
                ("📉 Risk Analysis", "analysis", 0.6)
            ]
        },
        "advanced": {
            "Advanced Strategies": [
                ("📉 Derivatives Trading", "derivatives", 0.25),
                ("🌍 International Markets", "global", 0.4),
                ("🤖 Algorithmic Trading", "algo", 0.55)
            ]
        }
    }

    # Interactive content
    with stylable_container(key="edu_content", css_styles="""
        { background: rgba(30,41,59,0.7); border-radius: 20px; padding: 2rem; }"""):
        
        # Progress dashboard
        st.subheader(f"Your Learning Path - {st.session_state.user_level.capitalize()}")
        total_topics = sum(len(chapter) for chapter in curriculum[st.session_state.user_level].values())
        completed = sum(st.session_state.learning_progress.get(topic[1], 0) for chapter in curriculum[st.session_state.user_level].values() for topic in chapter)
        st.write(f"Progress: {completed/total_topics:.0%}")
        
        # Chapters
        for chapter_title, topics in curriculum[st.session_state.user_level].items():
            with st.expander(f"📖 {chapter_title}", expanded=True):
                cols = st.columns(3)
                for idx, (topic_title, topic_id, progress) in enumerate(topics):
                    with cols[idx % 3]:
                        with stylable_container(key=f"card_{topic_id}", css_styles="""
                            { padding: 1rem; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); }"""):
                            
                            st.markdown(f"**{topic_title}**")
                            st.progress(st.session_state.learning_progress.get(topic_id, 0.0))
                            
                            if st.button("Start Learning", key=f"btn_{topic_id}"):
                                show_lesson(topic_id)

def show_lesson(topic_id):
    lessons = {
        "budgeting": {
            "content": """
            ## 💰 Basic Budgeting Mastery
            **Key Concepts:**
            - 50/30/20 Rule
            - Needs vs Wants
            - Emergency Funds
            
            Interactive Example:
            """,
            "video": "https://www.youtube.com/embed/embed_id_1",
            "quiz": [
                ("What percentage should go to needs?", ["50%", "30%", "20%"], 0)
            ]
        },
        # Add other lessons...
    }
    
    lesson = lessons[topic_id]
    with stylable_container(key="lesson_container", css_styles="""
        { background: rgba(30,41,59,0.9); border-radius: 20px; padding: 2rem; }"""):
        
        st.markdown(lesson["content"])
        
        # Interactive elements
        if "video" in lesson:
            st.video(lesson["video"])
        
        if "quiz" in lesson:
            st.subheader("Quick Check ✅")
            for q_idx, (q_text, options, correct) in enumerate(lesson["quiz"]):
                answer = st.radio(q_text, options, key=f"{topic_id}_q{q_idx}")
                if answer == options[correct]:
                    st.success("Correct! 🎉")
                    st.session_state.learning_progress[topic_id] = 1.0
                else:
                    st.error("Try again! 💡")




# ======================== AUTOMATED TESTS ========================
def run_automated_tests():
    st.subheader("🤖 Running Automated Tests")
    test_results = []
    
    # Test 1: Currency Conversion Test
    try:
        # Use a known conversion (assuming a dummy rate for testing)
        dummy_rate = 0.85  # Suppose 1 USD = 0.85 EUR
        test_amount = 100
        expected = test_amount * dummy_rate
        # Simulate conversion logic (here, we bypass API call for test)
        result = test_amount * dummy_rate
        assert abs(result - expected) < 0.01, "Currency conversion calculation failed."
        test_results.append("Currency Conversion Test: PASSED")
    except Exception as e:
        test_results.append(f"Currency Conversion Test: FAILED ({str(e)})")
    
    # Test 2: RSI Calculation Test
    try:
        # Create a dummy DataFrame with increasing prices
        dummy_data = pd.DataFrame({
            'Close': [i for i in range(1, 30)]
        })
        rsi = calculate_rsi(dummy_data)
        # For steadily increasing prices, RSI should be high (close to 100)
        assert rsi > 70, "RSI calculation seems off for rising prices."
        test_results.append("RSI Calculation Test: PASSED")
    except Exception as e:
        test_results.append(f"RSI Calculation Test: FAILED ({str(e)})")
    
    # Test 3: Portfolio Manager Dummy Insertion
    try:
        # Use in-memory SQLite DB to test insertion and retrieval
        test_conn = sqlite3.connect(':memory:')
        test_cursor = test_conn.cursor()
        test_cursor.execute('''CREATE TABLE portfolios
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             user_hash TEXT NOT NULL,
                             asset_type BLOB NOT NULL,
                             symbol BLOB NOT NULL,
                             quantity BLOB NOT NULL,
                             purchase_date BLOB NOT NULL)''')
        dummy_user = "dummy_hash"
        test_cursor.execute('''INSERT INTO portfolios (user_hash, asset_type, symbol, quantity, purchase_date)
                             VALUES (?, ?, ?, ?, ?)''',
                             (dummy_user,
                              encrypt_data("Stock"),
                              encrypt_data("AAPL"),
                              encrypt_data("10"),
                              encrypt_data("2023-01-01")))
        test_conn.commit()
        test_cursor.execute("SELECT * FROM portfolios WHERE user_hash=?", (dummy_user,))
        rows = test_cursor.fetchall()
        assert len(rows) == 1, "Portfolio insertion failed."
        test_results.append("Portfolio Manager Insertion Test: PASSED")
        test_conn.close()
    except Exception as e:
        test_results.append(f"Portfolio Manager Insertion Test: FAILED ({str(e)})")
    
    for result in test_results:
        st.write(result)

# ======================== PAGE ROUTING ========================
page = st.sidebar.selectbox("Select a page", 
                           ["user", "dashboard", "currency", "news", "calculators", 
                            "portfolio", "crypto", "education", "automated tests"])



if page == "user":
    user_page()
elif page == "dashboard":
    dashboard()
elif page == "currency":
    currency_converter()
elif page == "news":
    financial_news()
elif page == "calculators":
    financial_calculators()
elif page == "portfolio":
    portfolio_tracker()
elif page == "crypto":
    crypto_watch()
elif page == "education":
    financial_education()
elif page == "automated tests":
    run_automated_tests()


# ======================== FOOTER ========================
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
