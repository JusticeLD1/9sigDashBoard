import pandas as pd 

def get_symbol_data(file):
    df = pd.read_excel(file)
    positions = {}
    for index, row in df.iterrows():
        symbol = row['Symbol']
        cost = row['Average Cost']
        shares = row['Shares']
        
        #add to dict
        positions[symbol] = {"Average Cost" : cost, "Shares" : shares}

    return positions

