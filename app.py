import streamlit as st
import pandas as pd
import json
import os
import time

# --- CONFIGURATION ---
DATA_FILE = "bets_data.json"
ADMIN_PASSWORD = "keith"  # Type this in the sidebar to reveal admin controls

# --- HELPER FUNCTIONS ---
def load_data():
    if not os.path.exists(DATA_FILE):
        # Initialize with empty data if file doesn't exist
        return {"market_open": True, "bets": [], "result": None}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
         return {"market_open": True, "bets": [], "result": None}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# --- APP LAYOUT ---
st.set_page_config(page_title="Keith Coin Markets", page_icon="🪙")

# Load current state
data = load_data()

# Header
st.title("🪙 Keith Coin Prediction Market")
st.markdown("### Market: *How many slides are in this presentation?*")

# --- SIDEBAR (User Entry) ---
st.sidebar.header("Place Your Bet")

if data["market_open"]:
    with st.sidebar.form("bet_form"):
        user_name = st.text_input("Your Name")
        prediction = st.number_input("Your Guess (Number of Slides)", min_value=0, step=1)
        wager = st.slider("Wager (Keith Coins)", 1, 100, 10)
        
        submit = st.form_submit_button("Place Bet 🚀")
        
        if submit and user_name:
            new_bet = {
                "name": user_name,
                "prediction": int(prediction),
                "wager": wager,
                "timestamp": time.time()
            }
            data["bets"].append(new_bet)
            save_data(data)
            st.sidebar.success(f"Bet placed by {user_name}!")
            time.sleep(1)
            st.rerun()
else:
    st.sidebar.warning("🚫 Market is Closed!")

# --- MAIN DASHBOARD (Live Analytics) ---

# 1. Calculate Statistics
if data["bets"]:
    df = pd.DataFrame(data["bets"])
    total_pool = df['wager'].sum()
    total_bets = len(df)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Keith Coins Staked", f"🪙 {total_pool}")
    col2.metric("Active Traders", f"busts_in_silhouette {total_bets}")
    if not df.empty:
        col3.metric("Most Popular Guess", f"{df['prediction'].mode()[0]}")
    
    st.markdown("---")

    # 2. Visualization (The "Data Science" part)
    st.subheader("📊 Live Market Sentiment")
    # Simple bar chart of guesses
    chart_data = df['prediction'].value_counts().reset_index()
    chart_data.columns = ['Slide Count Guess', 'Count']
    st.bar_chart(chart_data, x='Slide Count Guess', y='Count')

    # Show recent ticker
    st.subheader("📜 Recent Transactions")
    st.dataframe(df[['name', 'prediction', 'wager']].tail(5), hide_index=True)

else:
    st.info("Waiting for the first bet...")


# --- ADMIN SECTION (Hidden) ---
st.markdown("---")
with st.expander("Admin / Presenter Tools"):
    password = st.text_input("Admin Password", type="password")
    
    if password == ADMIN_PASSWORD:
        st.success("Admin Access Granted")
        
        # Close Market Control
        if st.button("Toggle Market Open/Close"):
            data["market_open"] = not data["market_open"]
            save_data(data)
            st.rerun()
            
        st.write(f"Market Status: **{'OPEN' if data['market_open'] else 'CLOSED'}**")
        
        # SETTLEMENT
        st.divider()
        st.write("### 🏁 Settlement")
        actual_slides = st.number_input("Reveal Actual Slide Count", min_value=0)
        
        if st.button("Settlement & Pay Out"):
            data["market_open"] = False # Auto close
            data["result"] = actual_slides
            save_data(data)
            st.rerun()

# --- RESULTS SCREEN ---
if data["result"] is not None:
    st.balloons()
    st.markdown("## 🏆 MARKET RESOLVED!")
    st.markdown(f"### The actual number of slides was: **{data['result']}**")
    
    # Find winners
    df = pd.DataFrame(data["bets"])
    winners = df[df['prediction'] == data['result']]
    
    if not winners.empty:
        st.success(f"Congratulations to the {len(winners)} winner(s)!")
        for index, row in winners.iterrows():
            st.write(f"🎉 **{row['name']}** wins! (Bet: {row['wager']} KC)")
    else:
        st.error("No one guessed the exact number! The House (Keith) wins!")
    
    if st.button("Reset Everything"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.rerun()