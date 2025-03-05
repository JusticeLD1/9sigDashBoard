"""
rebalance gets price from start date compared to price now
it also tracks each quarter after start date as 9 sig aims to gain 9% per quarter 
"""
import pandas as pd


#determine how many quarter have passed since start date
def get_quarters(start_date):
    #get current date
    current_date = pd.to_datetime("today")
    #get difference in days
    days = (current_date - start_date).days
    return days // 90


def get_next_quarter(start_date):
    # Convert input to datetime if not already
    start_date = pd.to_datetime(start_date)

    # Get today's date
    today = pd.to_datetime("today").normalize()

    # Find the next quarter date from the start_date
    next_quarter_date = start_date

    # Keep adding 3 months (90 days approximation) until it's in the future
    while next_quarter_date <= today:
        next_quarter_date += pd.DateOffset(months=3)

    return next_quarter_date.normalize()  # Normalize to remove time component

def get_previous_quarter(get_next_quarter):
    #previous quarter = next quarter - 3 months 
    return get_next_quarter - pd.DateOffset(months=3)


def tqqq_quarterly_buy(current_shares, last_quarter_gain):
    """
    Calculate how many TQQQ shares to buy to ensure a 9% increase in holdings.

    :param current_shares: Number of TQQQ shares currently owned
    :param last_quarter_gain: Percentage gain/loss last quarter (e.g., -5 for -5%, 10 for +10%)
    :return: Shares to buy
    """

    # Convert gain percentage to decimal
    gain_decimal = last_quarter_gain / 100  

    # Calculate new target shares (increase by 9%)
    target_shares = current_shares * 1.09  

    # Calculate current adjusted shares based on last quarter’s performance
    current_adjusted_shares = current_shares * (1 + gain_decimal)

    # Shares to buy
    shares_to_buy = target_shares - current_adjusted_shares

    # If shares_to_buy is negative or zero, no need to buy more shares
    return round(shares_to_buy,2)


