import streamlit as st
import pandas as pd
import json
import os
import time

# --- CONFIGURATION ---
DATA_FILE = "bets_data.json"
ADMIN_PASSWORD = "keith" 
TARGET_SLIDES = 12  # The fixed answer

# --- CUSTOM CSS FOR "LIVE" PULSING EFFECT ---
st.set_page_config(page_title="Keith Coin Markets", page_icon="🪙", layout="wide")
st.markdown("""
    <style>
    .live-indicator {
        display: inline-block;
        width: 15px;
        height: 15px;
        background-color: red;
        border-radius: 50%;
        box-shadow: 0 0 0 0 rgba(255, 0, 0, 1);
        animation: pulse-red 2s infinite;
        vertical-align: middle;
        margin-right: 10px;
    }
    @keyframes pulse-red {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(255, 0, 0, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 0, 0, 0); }
    }
    .metric-box {
        padding: 10px;
        background-color: #f0f2f6;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 10px;
    }
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

# --- ADMIN SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Admin Panel")
    password = st.text_input("Admin Password", type="password")
    
    if password == ADMIN_PASSWORD:
        st.success("Unlocked")
        
        # 1. AUTO-REFRESH TOGGLE
        st.write("---")
        st.write("**Presentation Mode**")
        auto_refresh = st.checkbox("🔄 Auto-Refresh (Live View)", value=True)
        
        # 2. MARKET CONTROLS
        st.write("---")
        st.write("**Market Controls**")
        if st.button("Toggle Open/Close Market"):
            data["market_open"] = not data["market_open"]
            save_data(data)
            st.toast(f"Market is now {'OPEN' if data['market_open'] else 'CLOSED'}", icon="📢")
            time.sleep(0.5)
            st.rerun()

        # 3. SETTLEMENT (The Reveal)
        st.write("---")
        st.write("**🏁 Settlement**")
        # Defaulting to 12 as requested
        actual_slides = st.number_input("Correct Answer", value=TARGET_SLIDES)
        
        if st.button("🚨 RESOLVE MARKET"):
            data["market_open"] = False
            data["result"] = actual_slides
            save_data(data)
            st.rerun()

        # 4. NUCLEAR RESET
        st.write("---")
        if st.button("⚠️ HARD RESET (Delete All Data)"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.toast("System Wiped Clean", icon="🗑️")
            time.sleep(1)
            st.rerun()
    else:
        # Standard user view for sidebar
        st.info("Enter admin password to control the market.")
        
        # Add a refresh button for users in case they want to see updates
        if st.button("Refresh View"):
            st.rerun()

# --- MAIN APP UI ---

# Header with Live Indicator
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("🪙 Keith Coin Prediction Market")
    if data["market_open"]:
        st.markdown('<h4><span class="live-indicator"></span>LIVE MARKET: Slide Count</h4>', unsafe_allow_html=True)
    else:
        st.markdown('<h4>🔒 MARKET CLOSED</h4>', unsafe_allow_html=True)

# --- USER BETTING AREA (Top for mobile users) ---
if data["market_open"] and data["result"] is None:
    with st.expander("💸 PLACE YOUR BET HERE", expanded=True):
        with st.form("bet_form"):
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                user_name = st.text_input("Name")
            with c2:
                prediction = st.number_input("Guess # Slides", min_value=0, step=1)
            with c3:
                wager = st.slider("Wager (KC)", 10, 100, 50)
            
            submit = st.form_submit_button("🚀 Submit Order")
            
            if submit and user_name:
                new_bet = {
                    "name": user_name,
                    "prediction": int(prediction),
                    "wager": wager,
                    "timestamp": time.time()
                }
                data["bets"].append(new_bet)
                save_data(data)
                st.toast(f"Order filled for {user_name}!", icon="💰")
                time.sleep(0.5)
                st.rerun()

# --- LIVE DASHBOARD ---
if data["bets"]:
    df = pd.DataFrame(data["bets"])
    
    # 1. METRICS ROW
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Volume", f"🪙 {df['wager'].sum()}", "+12%")
    m2.metric("Active Traders", f"{len(df)}")
    if not df.empty:
        top_guess = df['prediction'].mode()[0]
        # Calculate percent of people who guessed the top guess
        consensus = (len(df[df['prediction'] == top_guess]) / len(df)) * 100
        m3.metric("Consensus Forecast", f"{top_guess} Slides")
        m4.metric("Market Confidence", f"{consensus:.0f}%")

    # 2. CHARTS & FEED
    c_chart, c_feed = st.columns([2, 1])
    
    with c_chart:
        st.subheader("📊 Order Book Distribution")
        chart_data = df['prediction'].value_counts().reset_index()
        chart_data.columns = ['Slide Count', 'Volume']
        st.bar_chart(chart_data, x='Slide Count', y='Volume', color="#ff4b4b")

    with c_feed:
        st.subheader("📜 Ticker")
        # Show latest 5 bets in reverse order
        latest = df.tail(8).iloc[::-1]
        for _, row in latest.iterrows():
            st.text(f"{row['name']} placed {row['wager']}KC on {row['prediction']}")

else:
    st.info("Waiting for liquidity... (Place a bet!)")


# --- RESOLUTION SCREEN ---
if data["result"] is not None:
    # ANIMATION TRIGGERS
    st.balloons()
    time.sleep(1)
    st.snow()
    
    st.divider()
    st.markdown(f"<h1 style='text-align: center; color: green;'>WINNING NUMBER: {data['result']}</h1>", unsafe_allow_html=True)
    
    df = pd.DataFrame(data["bets"])
    winners = df[df['prediction'] == data['result']]
    
    col_win, col_list = st.columns([1, 2])
    
    with col_win:
        st.markdown("### 🏆 Hall of Fame")
        if not winners.empty:
            total_payout = winners['wager'].sum() * 5  # Fun multiplier logic
            st.metric("Payout Multiplier", "5x")
            st.metric("Total Payout", f"🪙 {total_payout}")
        else:
            st.error("The House Wins! (No correct guesses)")
            
    with col_list:
        if not winners.empty:
            st.success(f"🎉 {len(winners)} Traders Guessed Correctly!")
            st.dataframe(winners[['name', 'wager']], use_container_width=True)


# --- AUTO-REFRESH LOGIC ---
# If admin has checked "Auto-Refresh" and we are not in the result phase (to avoid loop resets on win screen)
if 'auto_refresh' in locals() and auto_refresh and data["result"] is None:
    time.sleep(3)  # Refresh every 3 seconds
    st.rerun()