import modules
import modules.market_data

def portfolio_value(stock1,stock2,cash):
    stock1_value = modules.market_data.current_ticker_price(stock1[0]) * stock1[1]
    stock2_value = modules.market_data.current_ticker_price(stock2[0]) * stock2[1]
    
    #return total value
    return stock1_value + stock2_value + cash

