import pandas as pd

def get_symbol_data(file):
    # Check if file is None before trying to read it
    if file is None:
        return {"TQQQ": {"Average Cost": 0, "Shares": 0}}
    
    # Detect file type and read accordingly
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    
    positions = {}
    
    # Verify required columns exist
    required_columns = ['Symbol', 'Average Cost', 'Shares']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
    for index, row in df.iterrows():
        symbol = row['Symbol']
        cost = row['Average Cost']
        shares = row['Shares']
        
        # Add to dict
        positions[symbol] = {"Average Cost": cost, "Shares": shares}

    return positions