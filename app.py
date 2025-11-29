import streamlit as st
import pandas as pd
import json
import os
import time

# --- CONFIGURATION ---
DATA_FILE = "bets_data.json"
ADMIN_PASSWORD = "keith" 
TARGET_SLIDES = 12

# --- PAGE SETUP & AESTHETIC CSS ---
st.set_page_config(page_title="Keith Coin Markets", page_icon="🪙", layout="wide")

# Custom CSS for that "Dark Crypto" vibe
st.markdown("""
    <style>
    /* Main Background adjustments */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Card Styling */
    .css-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #41424C;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    
    /* Live Pulse Animation */
    .live-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        background-color: #00FF00;
        border-radius: 50%;
        box-shadow: 0 0 0 0 rgba(0, 255, 0, 1);
        animation: pulse-green 2s infinite;
        margin-right: 8px;
    }
    @keyframes pulse-green {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(0, 255, 0, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 0, 0); }
    }
    
    /* Leaderboard Styling */
    .leader-row {
        display: flex;
        justify-content: space-between;
        padding: 8px;
        border-bottom: 1px solid #333;
        font-family: monospace;
    }
    .leader-gold { color: #FFD700; font-weight: bold; }
    .leader-silver { color: #C0C0C0; font-weight: bold; }
    .leader-bronze { color: #CD7F32; font-weight: bold; }
    
    </style>
""", unsafe_allow_html=True)

# --- DATA FUNCTIONS ---
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

# --- ADMIN SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Admin Controls")
    password = st.text_input("Password", type="password")
    
    if password == ADMIN_PASSWORD:
        st.success("Admin Logged In")
        st.write("---")
        auto_refresh = st.checkbox("🔄 Auto-Refresh (Live Mode)", value=True)
        
        if st.button("⏯️ Open/Close Market"):
            data["market_open"] = not data["market_open"]
            save_data(data)
            st.rerun()
            
        st.write(f"Status: **{'OPEN' if data['market_open'] else 'CLOSED'}**")
        
        st.write("---")
        actual_slides = st.number_input("Result", value=TARGET_SLIDES)
        if st.button("🚨 RESOLVE & PAYOUT"):
            data["market_open"] = False
            data["result"] = actual_slides
            save_data(data)
            st.rerun()
            
        st.write("---")
        if st.button("⚠️ WIPE DATA (RESET)"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.rerun()

# --- MAIN HEADER ---
col_logo, col_status = st.columns([3, 1])
with col_logo:
    st.title("🪙 Keith Coin Markets")
with col_status:
    if data["market_open"]:
        st.markdown('<div style="text-align: right; padding-top: 20px;"><span class="live-indicator"></span>LIVE</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align: right; padding-top: 20px; color: red;">🛑 CLOSED</div>', unsafe_allow_html=True)

# --- BETTING CARD (Top Section) ---
if data["market_open"] and data["result"] is None:
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.markdown("### 📈 Place Your Prediction")
    st.markdown("**Market:** *How many slides are in this presentation?*")
    
    with st.form("bet_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
        with c1:
            user_name = st.text_input("Trader Name", placeholder="e.g. Elon")
        with c2:
            prediction = st.number_input("Your Guess", min_value=0, step=1)
        with c3:
            wager = st.slider("Wager (KC)", 10, 500, 50)
        with c4:
            st.markdown("<br>", unsafe_allow_html=True) # spacer
            submit = st.form_submit_button("BUY 🚀")
            
        if submit and user_name:
            new_bet = {
                "name": user_name,
                "prediction": int(prediction),
                "wager": wager,
                "timestamp": time.time()
            }
            data["bets"].append(new_bet)
            save_data(data)
            st.toast(f"Bet placed by {user_name}!", icon="💸")
            time.sleep(0.5)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# --- DASHBOARD AREA ---
if data["bets"]:
    df = pd.DataFrame(data["bets"])
    
    # METRICS
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Liquidity", f"🪙 {df['wager'].sum():,}")
    m2.metric("Active Traders", f"{len(df)}")
    m3.metric("Consensus", f"{df['prediction'].mode()[0]} Slides")
    
    st.markdown("---")
    
    # 2-COLUMN LAYOUT: CHART vs LEADERBOARD
    col_chart, col_leader = st.columns([2, 1])
    
    with col_chart:
        st.subheader("📊 Market Sentiment")
        # Customizing the chart color
        chart_data = df['prediction'].value_counts().reset_index()
        chart_data.columns = ['Slide Count', 'Volume']
        st.bar_chart(chart_data, x='Slide Count', y='Volume', color=["#00FF00"]) # Crypto Green
        
        # Recent Ticker
        with st.expander("📜 Recent Order Flow", expanded=False):
            st.dataframe(df[['name', 'prediction', 'wager']].tail(10).iloc[::-1], hide_index=True, use_container_width=True)

    with col_leader:
        st.subheader("🏆 Whale Leaderboard")
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        
        # Group by name to sum wagers (if someone bets twice)
        leaders = df.groupby('name')['wager'].sum().reset_index().sort_values('wager', ascending=False).head(5)
        
        for i, (index, row) in enumerate(leaders.iterrows()):
            rank = i + 1
            if rank == 1: style = "leader-gold"
            elif rank == 2: style = "leader-silver"
            elif rank == 3: style = "leader-bronze"
            else: style = ""
            
            st.markdown(f"""
                <div class="leader-row">
                    <span class="{style}">#{rank} {row['name']}</span>
                    <span>🪙 {row['wager']}</span>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Waiting for first trade...")

# --- RESULTS OVERLAY ---
if data["result"] is not None:
    st.markdown("---")
    st.balloons()
    
    # Winner Logic
    df = pd.DataFrame(data["bets"])
    winners = df[df['prediction'] == data['result']]
    
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background-color: #1a4d2e; border-radius: 15px; border: 2px solid #00ff00;">
        <h1>✅ ACTUAL SLIDE COUNT: {data['result']}</h1>
    </div>
    """, unsafe_allow_html=True)
    
    if not winners.empty:
        st.markdown("### 🎉 THE WINNERS")
        cols = st.columns(len(winners))
        for idx, row in winners.iterrows():
            st.success(f"🏆 {row['name']} wins! (Bet: {row['wager']} KC)")
    else:
        st.error("💀 The House Wins (No correct guesses).")


# --- AUTO REFRESH LOOP ---
if 'auto_refresh' in locals() and auto_refresh and data["result"] is None:
    time.sleep(2)
    st.rerun()