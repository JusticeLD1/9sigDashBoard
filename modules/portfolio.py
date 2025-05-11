import modules
import modules.market_data


def portfolio_value_csv(positions):
    total = 0 
    for i in positions:
        total += modules.market_data.current_ticker_price(i) * positions[i]["Shares"]
    return total

