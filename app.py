import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import modules.portfolio
import modules.market_data
import modules.rebalance
import modules.chart
import csvportion.parseCSVfile
import os
from modules.database import PortfolioDB
import modules.auth  # Import the auth module directly

# ---- Streamlit App Title ----
st.set_page_config(page_title="Portfolio Tracker", layout="wide")
st.title("📊 Portfolio Tracker Dashboard")

# Initialize database
os.makedirs("data", exist_ok=True)  # Create data directory if it doesn't exist
db = PortfolioDB("data/portfolio_app.db")

# Initialize authentication
auth = modules.auth.PortfolioAuth(db)  # Use the full module path

# Check if the user is logged in
if not auth.require_login():
    # If not logged in, the login form is displayed by require_login
    # and we stop execution here
    st.stop()

# After login
# Add logout button to sidebar
if st.sidebar.button("Log Out"):
    auth.logout()
    st.rerun()

# Display user information
username = auth.get_username()
user_data = auth.get_user_data()

# Display welcome message
st.sidebar.success(f"Welcome, {user_data['full_name']}!")

# Load user's portfolio data from database
portfolio = db.get_portfolio(username)
if portfolio:
    portfolio_data = portfolio['portfolio_data']
    cash_balance = portfolio['cash_balance']
    start_date = pd.to_datetime(portfolio['start_date'])
else:
    # Initialize with default empty portfolio
    portfolio_data = {"TQQQ": {"Average Cost": 0, "Shares": 0}}
    cash_balance = 1000
    start_date = pd.to_datetime("2024-01-01")
    # Create initial portfolio in database
    db.create_portfolio(username, portfolio_data, cash_balance, start_date.strftime("%Y-%m-%d"))

# Initialize session state for stock prices if not already done
if 'stock_prices' not in st.session_state:
    st.session_state.stock_prices = {}
    st.session_state.stock_prices['TQQQ'] = 0
    st.session_state.stock_prices['QQQ'] = 0

# Add refresh button in sidebar
if st.sidebar.button("🔄 Refresh Stock Prices"):
    try:
        # Only fetch prices for symbols we currently have
        for symbol in st.session_state.stock_prices.keys():
            st.session_state.stock_prices[symbol] = modules.market_data.current_ticker_price(symbol)
        st.sidebar.success("Stock prices updated!")
    except Exception as e:
        st.sidebar.error(f"Error updating prices: {str(e)}")

# ---- Sidebar - User Inputs ----
st.sidebar.header("⚙️ Portfolio Setup")

# Select Input Method (CSV or Manual Entry)
st.sidebar.subheader("📈 Main Stock Holdings")
csv_or_manual = st.sidebar.radio("Select input method", ["CSV", "Manual"])

# Strategy Start Date Selection
st.sidebar.subheader("📅 Strategy Start Date")
start_date = st.sidebar.date_input("Start Date", start_date)

# Additional Holdings
st.sidebar.subheader("💰 Additional Holdings")
cash_balance = st.sidebar.number_input("Excess Cash ($)", value=float(cash_balance), step=100.0, min_value=0.0)

# ---- Portfolio Holdings Input ----
if csv_or_manual == "CSV":
    # File uploader
    uploaded_file = st.sidebar.file_uploader("Upload CSV/Excel", type=["csv", "xlsx", "xls"])
    
    # Try to process the file if it exists
    if uploaded_file is not None:
        try:
            # Get portfolio data from file
            portfolio_data = csvportion.parseCSVfile.get_symbol_data(uploaded_file)
            
            # Update stock prices for any new symbols
            for symbol in portfolio_data.keys():
                if symbol not in st.session_state.stock_prices:
                    st.session_state.stock_prices[symbol] = 0
            
            # Save to database
            db.update_portfolio(username, portfolio_data)
            db.update_portfolio_settings(username, cash_balance, start_date.strftime("%Y-%m-%d"))
            
            # Display success message
            st.sidebar.success("File processed successfully!")
            st.sidebar.info("Click 'Refresh Stock Prices' to update current prices")
            
        except Exception as e:
            # Show error and reset to defaults
            st.sidebar.error(f"Error processing file: {str(e)}")
            portfolio_data = {"TQQQ": {"Average Cost": 0, "Shares": 0}}
else:
    # Manual Entry for Stock Holdings
    tqqq_shares = st.sidebar.number_input("TQQQ Shares", value=float(portfolio_data.get("TQQQ", {}).get("Shares", 0)), step=1.0, min_value=0.0)
    tqqq_cost = st.sidebar.number_input("TQQQ Average Cost", value=float(portfolio_data.get("TQQQ", {}).get("Average Cost", 0)), step=1.0, min_value=0.0)
    stock2 = st.sidebar.text_input("Stock 2 Ticker", value="QQQ").upper()
    stock2_shares = st.sidebar.number_input("Shares of Stock 2", value=float(portfolio_data.get(stock2, {}).get("Shares", 10)), step=1.0, min_value=0.0)
    stock2_cost = st.sidebar.number_input("Stock 2 Average Cost", value=float(portfolio_data.get(stock2, {}).get("Average Cost", 0)), step=1.0, min_value=0.0)
    
    # Add new symbol to stock prices if needed
    if stock2 not in st.session_state.stock_prices:
        st.session_state.stock_prices[stock2] = 0
    
    # Update portfolio data
    portfolio_data["TQQQ"] = {"Average Cost": tqqq_cost, "Shares": tqqq_shares}
    portfolio_data[stock2] = {"Average Cost": stock2_cost, "Shares": stock2_shares}
    
    # Save to database
    db.update_portfolio(username, portfolio_data)
    db.update_portfolio_settings(username, cash_balance, start_date.strftime("%Y-%m-%d"))

# ---- Portfolio Value Calculation ----
# Calculate portfolio value using stored prices
try:
    port_value = sum(
        details["Shares"] * st.session_state.stock_prices.get(symbol, 0)
        for symbol, details in portfolio_data.items()
    )
    port_value = round(port_value, 2)
except Exception as e:
    port_value = 0
    st.error(f"Error calculating portfolio value: {str(e)}")

# ---- Main Dashboard ----
st.markdown("---")
st.header("📌 Portfolio Overview")

# Display Portfolio Balance
st.subheader("💰 Portfolio Value")
if csv_or_manual == "Manual":
    st.metric(label="Total Portfolio Balance", value=f"${port_value:,.2f}")
else:
    if uploaded_file is not None:
        st.metric(label="Total Portfolio Balance", value=f"${port_value:,.2f}")
    else:
        st.info("Upload CSV/Excel file to view portfolio balance")

# ---- Portfolio Holdings Table ----
st.write("### 📌 Your Current Holdings")

# Convert portfolio_data dictionary to DataFrame for display
holdings_data = []
for symbol, details in portfolio_data.items():
    current_price = st.session_state.stock_prices.get(symbol, 0)
    holdings_data.append({
        "Symbol": symbol,
        "Shares": details.get("Shares", 0),
        "Average Cost": details.get("Average Cost", 0),
        "Current Price": current_price,
        "Total Value": round(details.get("Shares", 0) * current_price, 2)
    })
            
if holdings_data:
    df_portfolio = pd.DataFrame(holdings_data)
    st.table(df_portfolio)
else:
    st.info("Upload CSV/Excel file or input them to view your holdings")

# ---- Portfolio Performance & Adjustments ----
st.markdown("---")
st.header("📊 Portfolio Performance & Adjustments")

# Create Columns for Layout
col1, col2 = st.columns(2)

# Gain Percentage Calculation
with col1:
    st.subheader("📈 TQQQ Gain Percentage")
    try:
        gain_percentage = modules.market_data.get_percentage_change("TQQQ", start_date, pd.to_datetime("today"))
        st.metric(label=f"{"TQQQ"} Change Since Start", value=f"{gain_percentage:.2f}%")
    except Exception as e:
        st.warning(f"Unable to calculate gain percentage: {str(e)}")

# Quarters Passed Calculation
with col2:
    st.subheader("⏳ Quarters Elapsed")
    try:
        quarters = modules.rebalance.get_quarters(pd.to_datetime(start_date))
        st.metric(label="Quarters Passed", value=f"{quarters} quarters")
    except Exception as e:
        st.warning(f"Unable to calculate quarters: {str(e)}")

# ---- Rebalancing Status ----
st.subheader("🔄 Rebalancing Status")
try:
    next_quarter = modules.rebalance.get_next_quarter(pd.to_datetime(start_date))
    previous_quarter = modules.rebalance.get_previous_quarter(next_quarter)

    st.write(f"📅 **Next Quarter Ends:** {next_quarter}")
    st.write(f"📆 **Previous Quarter Ended:** {previous_quarter}")

    # Rebalancing Alert
    if pd.to_datetime("today").normalize() == next_quarter:
        st.warning("🔔 **Time to rebalance your portfolio!**")
    else:
        st.info("✅ No rebalancing needed at this time.")
        st.write("But if it were time to rebalance, here's what you'd do:")
except Exception as e:
    st.warning(f"Unable to calculate rebalancing dates: {str(e)}")

# ---- Rebalancing Suggestions ----
try:
    gain_percentage = modules.market_data.get_percentage_change("TQQQ", previous_quarter, next_quarter)
    st.write(f"📊 TQQQ has gained **{gain_percentage:.2f}%** since {previous_quarter}.")
    # Get TQQQ shares from portfolio_data
    tqqq_shares = portfolio_data.get("TQQQ", {}).get("Shares", 0)
    shares_to_buy_or_sell = modules.rebalance.tqqq_quarterly_buy(tqqq_shares, gain_percentage)
    st.success(f"📌 Adjustments: **Buy/Sell {shares_to_buy_or_sell} shares of TQQQ ** to maintain a 9% increase in holdings.")
except Exception as e:
    st.warning(f"⚠️ Unable to calculate rebalancing suggestions: {str(e)}")

# ---- Portfolio Progress Chart ----
st.markdown("---")
st.subheader("📉 Portfolio Progress Over Time")

# Generate Chart
try:
    fig = modules.chart.csv_chart(portfolio_data, start_date)
    st.pyplot(fig)
    plt.close(fig)  # Close the figure to free memory
except Exception as e:
    st.warning(f"⚠️ Unable to generate chart: {str(e)}")

# ---- Total Portfolio Value Chart ----
st.markdown("---")
st.subheader("📈 Total Portfolio Value Over Time")

# Generate chart based on input method
try:
    fig = modules.chart.total_value_chart(portfolio_data, start_date)
    if fig is not None:
        st.pyplot(fig)
        plt.close(fig)  # Close the figure to free memory
    else:
        st.info("📤 Please upload a CSV/Excel file to view your portfolio value chart.")
except Exception as e:
    st.error(f"⚠️ Unable to generate portfolio value chart: {str(e)}")
    
# Close any open plots to prevent memory issues
plt.close('all')