import streamlit as st
import pandas as pd
import json
import os
import time

# --- CONFIGURATION & STATE ---
DATA_FILE = "bets_data.json"
ADMIN_PASSWORD = "keith" 

# --- PAGE SETUP (Must be first) ---
st.set_page_config(page_title="Keith Duel", page_icon="⚔️", layout="wide")

# --- CUSTOM CSS (The "Duel" Look) ---
st.markdown("""
<style>
    /* 1. Main Background - Deep Navy */
    .stApp {
        background-color: #0b0e14;
        color: white;
    }
    
    /* 2. Sidebar - Slightly Lighter Navy */
    [data-testid="stSidebar"] {
        background-color: #11141d;
        border-right: 1px solid #2b2f42;
    }

    /* 3. Headers & Text */
    h1, h2, h3 {
        font-family: 'Source Sans Pro', sans-serif;
        color: #ffffff !important;
    }
    
    /* 4. Custom Cards (Mimicking the Game Cards) */
    div.css-1r6slb0 {
        background-color: #1a1d29;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #2b2f42;
    }

    /* 5. Metrics/Stats Containers */
    [data-testid="stMetricValue"] {
        color: #4f46e5; /* Electric Blue */
    }

    /* 6. Buttons (The "Wallet" Style) */
    .stButton>button {
        background-color: #4f46e5;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #4338ca;
        box-shadow: 0 0 10px #4f46e5;
    }
    
    /* 7. Input Fields (Dark Mode) */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #1a1d29;
        color: white;
        border: 1px solid #2b2f42;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
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

# --- TOP NAVBAR (Mimicking Image 1) ---
col_logo, col_space, col_wallet = st.columns([2, 6, 2])

with col_logo:
    st.title("⚔️ DUEL x KEITH")

with col_wallet:
    # Fake Wallet Button
    st.metric("My Wallet", "1,000 KC", delta=None)

st.markdown("---")

# --- MAIN HERO SECTION ---
# This mimics the "First Casino..." banner
st.markdown("""
<div style="background: linear-gradient(90deg, #1e1b4b 0%, #312e81 100%); padding: 40px; border-radius: 15px; text-align: center; margin-bottom: 30px; border: 1px solid #4f46e5;">
    <h1 style="font-size: 50px; margin-bottom: 10px;">The First Prediction Market</h1>
    <h3 style="color: #a5b4fc !important;">That Actually Matters for Your Grade.</h3>
    <p style="color: #c7d2fe;">Predict the slide count. Win Keith Coins. Glory awaits.</p>
</div>
""", unsafe_allow_html=True)

# --- TWO COLUMN LAYOUT (Betting on Left, Leaderboard on Right) ---
left_col, right_col = st.columns([1, 2])

# === LEFT COLUMN: THE "GAME" (Betting Interface) ===
with left_col:
    st.subheader("🎮 Live Market")
    
    # Wrap in a nice container
    with st.container(border=True):
        st.write("#### 📊 Event: Total Slides in Deck")
        
        if data["market_open"]:
            with st.form("bet_form"):
                st.write("Make your prediction below:")
                user_name = st.text_input("Username / Gamertag")
                prediction = st.number_input("Your Guess", min_value=0, step=1)
                wager = st.slider("Wager Amount (KC)", 10, 500, 50)
                
                submit = st.form_submit_button("🔥 PLACE BET")
                
                if submit and user_name:
                    new_bet = {
                        "name": user_name,
                        "prediction": int(prediction),
                        "wager": wager,
                        "timestamp": time.time()
                    }
                    data["bets"].append(new_bet)
                    save_data(data)
                    st.success(f"Bet placed for {user_name}!")
                    time.sleep(1)
                    st.rerun()
        else:
            st.error("🔒 MARKET CLOSED")
            if data["result"]:
                st.write(f"### RESULT: {data['result']} Slides")

# === RIGHT COLUMN: LEADERBOARD & STATS (Mimicking Image 3) ===
with right_col:
    st.subheader("🏆 Live Leaderboard")
    
    if data["bets"]:
        df = pd.DataFrame(data["bets"])
        
        # 1. Market Stats Row
        stat_c1, stat_c2, stat_c3 = st.columns(3)
        stat_c1.metric("Total Pool", f"{df['wager'].sum()} KC")
        stat_c2.metric("Players", len(df))
        if not df.empty:
            stat_c3.metric("Top Guess", f"{df['prediction'].mode()[0]}")
        
        # 2. The Leaderboard Table
        # We process the dataframe to look like a leaderboard
        leaderboard = df[['name', 'prediction', 'wager']].sort_values(by='wager', ascending=False).reset_index(drop=True)
        leaderboard.index += 1 # Start ranking at 1
        
        # Display nicely styled dataframe
        st.dataframe(
            leaderboard,
            column_config={
                "name": "Player",
                "prediction": "Guess",
                "wager": st.column_config.ProgressColumn(
                    "Wager Size",
                    help="Volume of Keith Coin staked",
                    format="%d KC",
                    min_value=0,
                    max_value=500,
                ),
            },
            use_container_width=True
        )
        
        # 3. Chart (Visuals)
        st.subheader("📈 Market Volume")
        chart_data = df['prediction'].value_counts().reset_index()
        chart_data.columns = ['Slide Count', 'Bets']
        st.bar_chart(chart_data, x='Slide Count', y='Bets', color="#4f46e5")
        
    else:
        st.info("Waiting for the first player to join the lobby...")

# --- ADMIN FOOTER (Hidden at bottom) ---
st.markdown("---")
with st.expander("🛠️ Admin Controls"):
    password = st.text_input("Password", type="password")
    if password == ADMIN_PASSWORD:
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Toggle Market Open/Close"):
                data["market_open"] = not data["market_open"]
                save_data(data)
                st.rerun()
        with col_b:
            actual_slides = st.number_input("Actual Result", min_value=0)
            if st.button("SETTLEMENT"):
                data["market_open"] = False
                data["result"] = actual_slides
                save_data(data)
                st.rerun()
                
        if st.button("Reset Game (Delete Data)"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.rerun()

# --- WINNER OVERLAY ---
if data["result"] is not None:
    st.balloons()
    df = pd.DataFrame(data["bets"])
    winners = df[df['prediction'] == data['result']]
    
    st.markdown(f"""
    <div style="background-color: #22c55e; padding: 20px; border-radius: 10px; text-align: center; color: black;">
        <h1>🎉 RESULT: {data['result']} SLIDES 🎉</h1>
    </div>
    """, unsafe_allow_html=True)
    
    if not winners.empty:
        st.write("### 💰 PAYOUTS")
        for i, row in winners.iterrows():
            st.success(f"PAYING OUT: {row['name']} wins {row['wager'] * 5} KC!")