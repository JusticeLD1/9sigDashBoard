import pandas as pd

def get_symbol_data(file):
    """
    Extract stock symbol data from an uploaded CSV or Excel file.
    
    Parameters:
    file: A file object uploaded through st.file_uploader
    
    Returns:
    Dictionary with stock symbols as keys and dictionaries of details as values
    """
    # Important: Check if file is None first, before any pandas operations
    if file is None:
        return {"TQQQ": {"Average Cost": 0, "Shares": 0}}
    
    try:
        # Detect file type based on extension
        file_extension = file.name.split('.')[-1].lower()
        
        if file_extension == 'csv':
            df = pd.read_csv(file)
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(file)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        # Verify required columns exist
        required_columns = ['Symbol', 'Average Cost', 'Shares']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Process each row into positions dictionary
        positions = {}
        for index, row in df.iterrows():
            symbol = row['Symbol']
            cost = row['Average Cost']
            shares = row['Shares']
            
            # Add to dict
            positions[symbol] = {"Average Cost": cost, "Shares": shares}
        
        return positions
        
    except Exception as e:
        # Log the error (could use a proper logging system in production)
        print(f"Error in get_symbol_data: {str(e)}")
        # Return a default portfolio on error
        return {"TQQQ": {"Average Cost": 0, "Shares": 0}}