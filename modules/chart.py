import numpy as np
import matplotlib.pyplot as plt
import modules.market_data


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

def total_value_chart(positions, start_date):
    #get stock data 
    stock_data = {}
    for stock in positions:
        stock_data[stock] = modules.market_data.get_stock_data(stock, start_date)
    
    #create figure
    fig, ax = plt.subplots(figsize=(12, 6))

    #plot stock data on axes
    total_value = np.zeros(len(stock_data[stock]))
    for stock in stock_data:
        total_value += stock_data[stock]["Close"] * positions[stock]["Shares"]
    
    ax.plot(stock_data[stock].index, total_value, label="Total Value")
    ax.set_title("Total Portfolio Value Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value")
    ax.legend()
    
    #return figure object
    return fig


#testing 
positions = {"TQQQ": {"Shares": 100}, "QQQ": {"Shares": 10}, "AAPL": {"Shares": 5}}
start_date = "2024-01-01"
csv_chart(positions, start_date)