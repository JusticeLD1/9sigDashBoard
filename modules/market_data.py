import yfinance as yf 
import pandas as pd

def current_ticker_price(ticker):  
    '''
    closing value of chosen ticker
    '''
    # fetch ticker data 
    stock = yf.Ticker(str(ticker))
    
    #closing price of the stock
    stock_price = stock.history(period='1d')["Close"].iloc[-1]

    return stock_price


test = current_ticker_price("AAPL")
print(test)

def get_percentage_change(stock: str, start_date: str, end_date: str):
    # Download stock data
    data = yf.download(stock, start=start_date, end=end_date)
    
    if data.empty:
        return f"No data available for {stock} between {start_date} and {end_date}"
    
    # Get the closing prices for the start and end dates
    start_price = data["Close"].iloc[0]
    end_price = data["Close"].iloc[-1]
    
    # Calculate percentage change
    percentage_change = ((end_price - start_price) / start_price) * 100
    
    return float(percentage_change.round(2))


def get_stock_data(stock: str, start_date: str):
    # Download stock data
    data = yf.download(stock, start=start_date)
    
    return data