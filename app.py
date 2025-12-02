import streamlit as st
import pandas as pd
import json
import os
import time
import base64
import plotly.express as px

# --- CONFIGURATION ---
DATA_FILE = "bets_data.json"
ADMIN_PASSWORD = "keith" 
TARGET_SLIDES = 38
IMAGE_PATH = "keithcoin.png"

# --- HELPER: CONVERT IMAGE TO STRING FOR HTML ---
def get_base64_image(image_path):
    if not os.path.exists(image_path):
        return "" # Fail gracefully if image is missing
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Convert your image for use in the Wallet/Header
img_b64 = get_base64_image(IMAGE_PATH)

# --- PAGE SETUP ---
# We try to use the image as the browser tab icon, fallback to emoji if missing
try:
    st.set_page_config(page_title="Keith Coin | Duel", page_icon=IMAGE_PATH, layout="wide")
except:
    st.set_page_config(page_title="Keith Coin | Duel", page_icon="🪙", layout="wide")

# --- CUSTOM CSS (THE DUEL AESTHETIC) ---
st.markdown(f"""
    <style>
    /* 1. BACKGROUND - Deep Dark Navy */
    .stApp {{
        background-color: #0b0e11;
        color: white;
    }}
    
    /* 2. SIDEBAR - Chat Style */
    section[data-testid="stSidebar"] {{
        background-color: #1a1d26;
        border-right: 1px solid #2d303e;
    }}
    
    /* 3. CARD STYLING */
    .duel-card {{
        border-radius: 15px;
        padding: 20px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }}
    .card-purple {{ background: linear-gradient(135deg, #6b2cf5 0%, #4c1db0 100%); }}
    .card-orange {{ background: linear-gradient(135deg, #ff9f43 0%, #ee5253 100%); }}
    .card-blue {{ background: linear-gradient(135deg, #0abde3 0%, #5f27cd 100%); }}

    /* 4. WALLET BUTTON WITH CUSTOM IMAGE */
    .wallet-btn {{
        background-color: #2d3240;
        color: #fff;
        padding: 10px 20px;
        border-radius: 12px;
        font-weight: bold;
        float: right;
        border: 1px solid #4b4b4b;
        display: flex;
        align-items: center;
        gap: 10px;
        font-family: monospace;
        font-size: 16px;
    }}
    
    /* 5. CHAT MESSAGE STYLE */
    .chat-msg {{
        font-size: 13px;
        margin-bottom: 8px;
        border-bottom: 1px solid #2d303e;
        padding-bottom: 4px;
    }}
    .chat-user {{ color: #5f27cd; font-weight: bold; margin-right: 5px; }}
    .chat-text {{ color: #b2bec3; }}
    
    /* Circular Image Styling */
    .coin-icon {{
        width: 30px;
        height: 30px;
        border-radius: 50%;
        vertical-align: middle;
    }}
    </style>
""", unsafe_allow_html=True)

# --- DATA HANDLING ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"market_open": True, "bets": [], "result": None}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
         return {"market_open": True, "bets": [], "result": None}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()

# --- SIDEBAR (LOGO + CHAT) ---
with st.sidebar:
    # DISPLAY BIG LOGO
    if os.path.exists(IMAGE_PATH):
        st.image(IMAGE_PATH, width=150)
    else:
        st.header("🪙 Keith Coin")

    st.markdown("### 🟢 Live Bets")
    
    if data["bets"]:
        df = pd.DataFrame(data["bets"])
        recent = df.tail(15).iloc[::-1]
        for _, row in recent.iterrows():
            st.markdown(f"""
                <div class="chat-msg">
                    <span class="chat-user">{row['name']}</span>
                    <span class="chat-text">wagered {row['wager']} <img src="data:image/png;base64,{img_b64}" width="15" style="vertical-align:middle"></span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("*Chat is quiet...*")
    
    # Hidden Admin Controls
    st.markdown("---")
    with st.expander("🛠️ Admin Controls", expanded=False):
        password = st.text_input("Key", type="password")
        if password == ADMIN_PASSWORD:
            auto_refresh = st.checkbox("Live Feed", value=True)
            if st.button("Open/Close Market"):
                data["market_open"] = not data["market_open"]
                save_data(data)
                st.rerun()
            if st.button("RESET ALL"):
                if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
                st.rerun()
            actual_slides = st.number_input("Result", value=TARGET_SLIDES)
            if st.button("RESOLVE"):
                data["market_open"] = False
                data["result"] = actual_slides
                save_data(data)
                st.rerun()

# --- MAIN HEADER & WALLET ---
col_title, col_wallet = st.columns([3, 2])

with col_title:
    st.markdown("# ⚔️ Keith Coin Markets")

with col_wallet:
    total_pool = sum(b['wager'] for b in data['bets']) if data['bets'] else 0
    # Custom HTML Button with the Image embedded via Base64
    st.markdown(f"""
        <div class="wallet-btn">
            <span>POOL:</span>
            <img src="data:image/png;base64,{img_b64}" class="coin-icon">
            <span style="color: #00FF00;">{total_pool}</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- GAME CARDS ---
if data["result"] is None:
    c1, c2, c3 = st.columns(3)

    # 1. BETTING
    with c1:
        st.markdown('<div class="duel-card card-purple"><h3>🎲 Place Bet</h3></div>', unsafe_allow_html=True)
        if data["market_open"]:
            with st.container(border=True):
                with st.form("bet_form", clear_on_submit=True):
                    name = st.text_input("Username")
                    guess = st.number_input("Coin Prediction", min_value=0)
                    wager = st.slider("Wager Amount", 10, 100, 50)
                    if st.form_submit_button("BET NOW"):
                        if name:
                            data["bets"].append({
                                "name": name, 
                                "prediction": int(guess), 
                                "wager": wager, 
                                "timestamp": time.time()
                            })
                            save_data(data)
                            st.rerun()
        else:
            st.warning("Market Closed")

    # 2. CHART
    with c2:
        st.markdown('<div class="duel-card card-orange"><h3>📊 Live Stats</h3></div>', unsafe_allow_html=True)
        with st.container(border=True):
            if data["bets"]:
                df = pd.DataFrame(data["bets"])
                #chart_data = df['prediction'].value_counts().reset_index()
                #chart_data.columns = ['Count', 'Volume']
                #st.scatter_chart(df, x='Count', y='Volume', color="#ff9f43")
                fig = px.scatter(df, x="prediction", y="wager", text="name")
                fig.update_traces(textposition='top center')

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("No data yet.")

    # 3. LEADERBOARD
    with c3:
        st.markdown('<div class="duel-card card-blue"><h3>🏆 Whales</h3></div>', unsafe_allow_html=True)
        with st.container(border=True):
            if data["bets"]:
                df = pd.DataFrame(data["bets"])
                leaders = df.groupby('name')['wager'].sum().sort_values(ascending=False).head(5)
                # Custom formatting for leaderboard to include the coin icon
                for name, w in leaders.items():
                    st.markdown(f"**{name}** — {w} KC")
            else:
                st.write("Be the first whale.")

# --- RESULTS POPUP ---
else:
    st.balloons()
    st.markdown(f"""
        <div style="text-align: center; padding: 50px; background: #1a1d26; border-radius: 20px; border: 2px solid #00ff00;">
            <img src="data:image/png;base64,{img_b64}" style="width: 100px; border-radius: 50%; margin-bottom: 20px;">
            <h1 style="color: #00ff00; font-size: 60px;">ANSWER: {data['result']}</h1>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🤑 Winners Payout")
    df = pd.DataFrame(data["bets"])
    winners = df[df['prediction'] == data['result']]
    if not winners.empty:
        st.dataframe(winners[['name', 'wager']], use_container_width=True)
    else:
        st.error("House Wins.")

# --- AUTO REFRESH ---
if 'auto_refresh' in locals() and auto_refresh and data["result"] is None:
    time.sleep(2)
    st.rerun()
