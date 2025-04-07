import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import modules
import modules.portfolio
import modules.market_data
import modules.rebalance
import modules.chart
import csvportion.parseCSVfile

# ---- Streamlit App Title ----
st.set_page_config(page_title="Portfolio Tracker", layout="wide")
st.title("📊 Portfolio Tracker Dashboard")

# ---- Sidebar - User Inputs ----
st.sidebar.header("⚙️ Portfolio Setup")

# Select Input Method (CSV or Manual Entry)
st.sidebar.subheader("📈 Main Stock Holdings")
csv_or_manual = st.sidebar.radio("Select input method", ["CSV", "Manual"])

# Strategy Start Date Selection
st.sidebar.subheader("📅 Strategy Start Date")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2024-01-01"))

# Additional Holdings
st.sidebar.subheader("💰 Additional Holdings")
cash_balance = st.sidebar.number_input("Excess Cash ($)", value=1000, step=100, min_value=0)

# ---- Portfolio Holdings Input ----
portfolio_data2 = {"TQQQ": {"Average Cost": 0, "Shares": 0}}  # Default empty portfolio

if csv_or_manual == "CSV":
    uploaded_file = st.sidebar.file_uploader("Upload CSV/Excel", type=["csv", "xlsx", "xls"])
    stock_1 = "TQQQ"
    shares_1 = 0  # Default value
    
    # Only try to process the file if it's actually uploaded
    if uploaded_file is not None:
        try:
            portfolio_data2 = csvportion.parseCSVfile.get_symbol_data(uploaded_file)
            if "TQQQ" in portfolio_data2:
                shares_1 = portfolio_data2["TQQQ"]["Shares"]
            else:
                shares_1 = 0
        except Exception as e:
            st.sidebar.error(f"Error parsing file: {str(e)}")
            # Reset to default if there's an error
            portfolio_data2 = {"TQQQ": {"Average Cost": 0, "Shares": 0}}
            shares_1 = 0
    else:
        # Set default portfolio when no file is uploaded
        portfolio_data2 = {"TQQQ": {"Average Cost": 0, "Shares": 0}}
        shares_1 = 0
else:
    # Manual Entry for Stock Holdings
    stock_1 = st.sidebar.text_input("Stock 1 Ticker", value="TQQQ").upper()
    shares_1 = st.sidebar.number_input("Shares of Stock 1", value=100, step=1, min_value=0)
    stock_2 = st.sidebar.text_input("Stock 2 Ticker", value="QQQ").upper()
    shares_2 = st.sidebar.number_input("Shares of Stock 2", value=10, step=1, min_value=0)

# ---- Portfolio Value Calculation ----
if csv_or_manual == "Manual":
    risky_stock = [stock_1, shares_1]
    base_stock = [stock_2, shares_2]
    port_value = round(modules.portfolio.portfolio_value(risky_stock, base_stock, cash_balance), 2)
else:
    # Only calculate portfolio value if file was uploaded
    if uploaded_file is not None:
        try:
            port_value = round(modules.portfolio.portfolio_value_csv(portfolio_data2), 2)
        except Exception as e:
            port_value = 0
            st.error(f"Error calculating portfolio value: {str(e)}")
    else:
        port_value = 0

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
if csv_or_manual == "Manual":
    portfolio_data = {
        "Stock": [stock_1, stock_2],
        "Shares Held": [shares_1, shares_2],
        "Excess Cash": [f"${cash_balance:,.2f}", ""]
    }
    df_portfolio = pd.DataFrame(portfolio_data)
    st.table(df_portfolio)
else:
    if uploaded_file is not None:
        try:
            # Convert portfolio_data2 dictionary to DataFrame for display
            holdings_data = []
            for symbol, details in portfolio_data2.items():
                holdings_data.append({
                    "Symbol": symbol,
                    "Shares": details.get("Shares", 0),
                    "Average Cost": details.get("Average Cost", 0)
                })
            
            if holdings_data:
                df_portfolio2 = pd.DataFrame(holdings_data)
                st.table(df_portfolio2)
            else:
                st.info("No holdings found in the uploaded file")
        except Exception as e:
            st.error(f"Error displaying holdings: {str(e)}")
    else:
        st.info("Upload CSV/Excel file to view your holdings")

# ---- Portfolio Performance & Adjustments ----
st.markdown("---")
st.header("📊 Portfolio Performance & Adjustments")

# Create Columns for Layout
col1, col2 = st.columns(2)

# Gain Percentage Calculation
with col1:
    st.subheader("📈 TQQQ Gain Percentage")
    try:
        gain_percentage = modules.market_data.get_percentage_change(stock_1, start_date, pd.to_datetime("today"))
        st.metric(label=f"{stock_1} Change Since Start", value=f"{gain_percentage:.2f}%")
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
    gain_percentage = modules.market_data.get_percentage_change(stock_1, previous_quarter, next_quarter)
    st.write(f"📊 {stock_1} has gained **{gain_percentage:.2f}%** since {previous_quarter}.")
    shares_to_buy_or_sell = modules.rebalance.tqqq_quarterly_buy(shares_1, gain_percentage)
    st.success(f"📌 Adjustments: **Buy/Sell {shares_to_buy_or_sell} shares of {stock_1}** to maintain a 9% increase in holdings.")
except Exception as e:
    st.warning(f"⚠️ Unable to calculate rebalancing suggestions: {str(e)}")

# ---- Portfolio Progress Chart ----
st.markdown("---")
st.subheader("📉 Portfolio Progress Over Time")

# Generate Chart
if csv_or_manual == "Manual":
    try:
        fig = modules.chart.manual_chart(risky_stock, base_stock, start_date)
        st.pyplot(fig)
        plt.close(fig)  # Close the figure to free memory
    except Exception as e:
        st.warning(f"⚠️ Unable to generate chart: {str(e)}")
else:
    if uploaded_file is not None:
        try:
            fig = modules.chart.csv_chart(portfolio_data2, start_date)
            st.pyplot(fig)
            plt.close(fig)  # Close the figure to free memory
        except Exception as e:
            st.warning(f"⚠️ Unable to generate chart: {str(e)}")
    else:
        st.info("Upload CSV/Excel file to view portfolio progress chart")

# ---- Total Portfolio Value Chart ----
st.markdown("---")
st.subheader("📈 Total Portfolio Value Over Time")

# Generate chart based on input method
try:
    if csv_or_manual == "Manual":
        fig = modules.chart.manual_total_value_chart(
            [stock_1, shares_1],
            [stock_2, shares_2],
            cash_balance,
            start_date
        )
        if fig is not None:
            st.pyplot(fig)
            plt.close(fig)  # Close the figure to free memory
    else:  # CSV method
        if uploaded_file is not None:
            fig = modules.chart.total_value_chart(portfolio_data2, start_date)
            if fig is not None:
                st.pyplot(fig)
                plt.close(fig)  # Close the figure to free memory
        else:
            st.info("📤 Please upload a CSV/Excel file to view your portfolio value chart.")
except Exception as e:
    st.error(f"⚠️ Unable to generate portfolio value chart: {str(e)}")
    
# Close any open plots to prevent memory issues
plt.close('all')