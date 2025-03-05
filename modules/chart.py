import numpy as np
import matplotlib.pyplot as plt
import modules.market_data 

import matplotlib.pyplot as plt

def chart(stock1, stock2, start_date):
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

