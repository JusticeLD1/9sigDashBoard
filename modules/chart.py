import numpy as np
import matplotlib.pyplot as plt
import modules.market_data
import pandas as pd


def manual_chart(stock1, stock2, start_date):
    # 1) Get stock data
    stock1_data = modules.market_data.get_stock_data(stock1[0], start_date)
    stock2_data = modules.market_data.get_stock_data(stock2[0], start_date)

    # 2) Create a figure and axes using subplots
    fig, ax = plt.subplots(figsize=(12, 6))

    # 3) Plot stock data on our axes
    ax.plot(stock1_data["Close"] * stock1[1], label=stock1[0])
    ax.plot(stock2_data["Close"] * stock2[1], label=stock2[0])
    ax.set_title(f"{stock1[0]} vs {stock2[0]}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value")
    ax.legend()

    # 4) Return the figure object (and/or axes if you want)
    return fig

def csv_chart(positions, start_date):
    #get stock data of tqqq and other stocks
    stock_data = {}
    for stock in positions:
        stock_data[stock] = modules.market_data.get_stock_data(stock, start_date)
    
    #create figure
    fig, ax = plt.subplots(figsize=(12, 6))

    #plot stock data on axes
    for stock in stock_data:
        ax.plot(stock_data[stock]["Close"] * positions[stock]["Shares"], label=stock)
    ax.set_title("Portfolio Value Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value")
    ax.legend()

    #return figure object
    return fig 


def manual_total_value_chart(stock1, stock2, cash_balance, start_date):
    """
    Create a chart showing total portfolio value over time for manually entered holdings.
    
    Parameters:
    - stock1: List containing [ticker_symbol, shares]
    - stock2: List containing [ticker_symbol, shares]
    - cash_balance: Float representing cash holdings
    - start_date: Starting date for chart data
    
    Returns:
    - Matplotlib figure object
    """
    # Close any existing figures to prevent memory issues
    plt.close('all')
    
    # Get stock data
    stock1_data = modules.market_data.get_stock_data(stock1[0], start_date)
    stock2_data = modules.market_data.get_stock_data(stock2[0], start_date)
    
    # Ensure data is available
    if stock1_data is None or stock2_data is None or stock1_data.empty or stock2_data.empty:
        raise ValueError(f"No data available for {stock1[0]} or {stock2[0]}")
    
    # Align dates for both stocks
    common_dates = stock1_data.index.intersection(stock2_data.index)
    if len(common_dates) == 0:
        raise ValueError("No common dates found between stocks")
    
    stock1_data = stock1_data.loc[common_dates]
    stock2_data = stock2_data.loc[common_dates]
    
    # Create a new figure and clear the current figure to avoid duplicate legends
    plt.clf()
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.tight_layout(pad=4.0)
    
    # Calculate components of portfolio value
    stock1_values = stock1_data["Close"] * stock1[1]
    stock2_values = stock2_data["Close"] * stock2[1]
    
    # Add constant cash balance
    cash_series = pd.Series(cash_balance, index=common_dates)
    
    # Calculate total portfolio value
    total_value = stock1_values + stock2_values + cash_series
    
    # Plot the data (using a single plot call for total value)
    ax.plot(common_dates, total_value, label="Total Portfolio Value", linewidth=2.5, color='blue')
    
    # Add individual components as thinner lines
    ax.plot(common_dates, stock1_values, label=f"{stock1[0]} Value", linewidth=1, alpha=0.7)
    ax.plot(common_dates, stock2_values, label=f"{stock2[0]} Value", linewidth=1, alpha=0.7)
    ax.plot(common_dates, cash_series, label="Cash", linewidth=1, alpha=0.7, linestyle='--')
    
    # Add labels and styling
    ax.set_title("Total Portfolio Value Over Time", fontsize=14, fontweight='bold')
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Value ($)", fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # Create a proper legend (use loc='best' to automatically find the best placement)
    ax.legend(loc='best')
    
    # Format y-axis as dollars
    ax.yaxis.set_major_formatter('${x:,.0f}')
    
    # Return the figure
    return fig


def total_value_chart(positions, start_date):
    """
    Create a chart showing total portfolio value over time for CSV-imported holdings.
    
    Parameters:
    - positions: Dictionary of stock positions from CSV
    - start_date: Starting date for chart data
    
    Returns:
    - Matplotlib figure object
    """
    # Close any existing figures
    plt.close('all')
    
    # Get stock data for each position
    stock_data = {}
    for stock in positions:
        data = modules.market_data.get_stock_data(stock, start_date)
        if data is not None and not data.empty:
            stock_data[stock] = data
    
    if not stock_data:
        raise ValueError("No valid stock data available")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.tight_layout(pad=4.0)
    
    # Use the first stock's dates as a reference
    reference_stock = list(stock_data.keys())[0]
    date_range = stock_data[reference_stock].index
    
    # Create a dictionary to store values per date for each stock
    value_by_date = {}
    
    # Initialize total value array
    total_values = np.zeros(len(date_range))
    
    # Plot individual stock values
    for i, date in enumerate(date_range):
        for stock in stock_data:
            if date in stock_data[stock].index:
                # Get stock price for this date
                price = stock_data[stock].loc[date, "Close"]
                shares = positions[stock]["Shares"]
                value = price * shares
                
                # Store value for plotting later
                if stock not in value_by_date:
                    value_by_date[stock] = np.zeros(len(date_range))
                value_by_date[stock][i] = value
                
                # Add to total for this date
                total_values[i] += value
    
    # Plot each stock's value
    for stock in value_by_date:
        ax.plot(date_range, value_by_date[stock], 
                label=f"{stock}", 
                linewidth=1, alpha=0.6)
    
    # Plot total portfolio value
    ax.plot(date_range, total_values, 
            label=f"Total Value", 
            linewidth=2.5, color='blue')
    
    # Add labels and styling
    ax.set_title("Total Portfolio Value Over Time", fontsize=14, fontweight='bold')
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Value ($)", fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best')
    
    # Format y-axis as dollars
    from matplotlib.ticker import FuncFormatter
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    return fig