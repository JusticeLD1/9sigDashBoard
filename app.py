import streamlit as st
import pandas as pd
import modules
import modules.portfolio
import modules.market_data
import modules.rebalance
import modules.chart

# ---- Streamlit App Title ----
st.set_page_config(page_title="Portfolio Tracker", layout="wide")
st.title("📊 Portfolio Tracker Dashboard")

# ---- Sidebar - User Inputs ----
st.sidebar.header("⚙️ Portfolio Setup")

# Main Stock Holdings
st.sidebar.subheader("📈 Main Stock Holdings")
stock_1 = st.sidebar.text_input("Stock 1 Ticker", value="TQQQ").upper()
shares_1 = st.sidebar.number_input("Shares of Stock 1", value=100, step=1, min_value=0)

stock_2 = st.sidebar.text_input("Stock 2 Ticker", value="QQQ").upper()
shares_2 = st.sidebar.number_input("Shares of Stock 2", value=20, step=1, min_value=0)

# Additional Holdings
st.sidebar.subheader("💰 Additional Holdings")
cash_balance = st.sidebar.number_input("Excess Cash ($)", value=1000, step=100, min_value=0)

# Portfolio Value Calculation
risky_stock = [stock_1, shares_1]
base_stock = [stock_2, shares_2]
port_value = modules.portfolio.portfolio_value(risky_stock, base_stock, cash_balance)
port_value = round(port_value, 2)

# Strategy Start Date
st.sidebar.subheader("📅 Strategy Start Date")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2024-01-01"))

# ---- Main Dashboard ----
st.markdown("---")
st.header("📌 Portfolio Overview")

# Display Portfolio Balance
st.subheader("💰 Portfolio Value")
st.metric(label="Total Portfolio Balance", value=f"${port_value:,}")

# ---- Portfolio Holdings ----
st.write("### 📌 Your Current Holdings")
portfolio_data = {
    "Stock": [stock_1, stock_2],
    "Shares Held": [shares_1, shares_2],
    "Excess Cash": [f"${cash_balance:,}", ""]
}
df_portfolio = pd.DataFrame(portfolio_data)
st.table(df_portfolio)

# ---- Gain Percentage & Rebalancing ----
st.markdown("---")
st.header("📊 Portfolio Performance & Adjustments")

# Columns for better layout
col1, col2 = st.columns(2)

# Gain Percentage
with col1:
    st.subheader("📈 Gain Percentage")
    try:
        gain_percentage = modules.market_data.get_percentage_change(stock_1, start_date, pd.to_datetime("today"))
        st.metric(label=f"{stock_1} Change Since Start", value=f"{gain_percentage:.2f}%")
    except:
        st.warning("Please enter a valid start date.")

# Quarters Passed
with col2:
    st.subheader("⏳ Quarters Elapsed")
    try:
        quarters = modules.rebalance.get_quarters(pd.to_datetime(start_date))
        st.metric(label="Quarters Passed", value=f"{quarters} quarters")
    except:
        st.warning("Please enter a valid start date.")

# ---- Rebalancing Status ----
st.subheader("🔄 Rebalancing Status")
next_quarter = modules.rebalance.get_next_quarter(pd.to_datetime(start_date))
previous_quarter = modules.rebalance.get_previous_quarter(next_quarter)

st.write(f"📅 **Next Quarter Ends:** {next_quarter}")
st.write(f"📆 **Previous Quarter Ended:** {previous_quarter}")

# Display rebalancing suggestions if the quarter has ended
if pd.to_datetime("today").normalize() == next_quarter:
    st.warning("🔔 **Time to rebalance your portfolio!**")
else:
    st.info("✅ No rebalancing needed at this time.")
    st.write("But if it were time to rebalance, here’s what you’d do:")

# ---- Rebalancing Suggestions ----
try:
    gain_percentage = modules.market_data.get_percentage_change(stock_1, previous_quarter, next_quarter)
    st.write(f"📊 {stock_1} has gained **{gain_percentage:.2f}%** since {previous_quarter}.")
    
    shares_to_buy_or_sell = modules.rebalance.tqqq_quarterly_buy(shares_1, gain_percentage)
    st.success(f"📌 Adjustments: **Buy/Sell {shares_to_buy_or_sell} shares of {stock_1}** to maintain a 9% increase in holdings.")
except:
    st.warning("⚠️ Please enter a valid start date to track gain percentage.")

# ---- Portfolio Progress Chart ----
st.markdown("---")
st.subheader("📉 Portfolio Progress Over Time")

try:
    fig = modules.chart.chart(risky_stock, base_stock, start_date)
    st.pyplot(fig)
except:
    st.warning("⚠️ Unable to generate chart. Ensure stock tickers are correct.")
