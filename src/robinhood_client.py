import os
import getpass
import time
from dotenv import load_dotenv
import robin_stocks.robinhood as rh
import pandas as pd

def login_to_robinhood():
    """
    Log in to Robinhood using credentials from .env file.
    """
    load_dotenv()
    username = os.getenv("ROBINHOOD_USERNAME")
    password = os.getenv("ROBINHOOD_PASSWORD")
    
    if not username or not password:
        print("Error: Robinhood credentials not found in .env file")
        return False
    
    print("Initiating login to Robinhood...")
    
    try:
        # Initial login attempt to trigger SMS
        rh.login(username, 
                password,
                expiresIn=86400,
                store_session=True,
                by_sms=False)  # Enable SMS authentication
        
        print("Successfully logged in to Robinhood!")
        return True
            
    except Exception as e:
        print(f"Login failed: {str(e)}")
        print("Please make sure you entered the correct SMS code.")
        return False

def get_portfolio_data():
    """
    Fetch portfolio data from Robinhood
    """
    # Get stock positions
    my_stocks = rh.build_holdings()
    
    # Convert to DataFrame for easier manipulation
    stocks_df = pd.DataFrame.from_dict(my_stocks, orient='index')
    
    # Convert numeric columns
    numeric_cols = ['price', 'quantity', 'average_buy_price', 'equity', 'percent_change', 'equity_change']
    for col in numeric_cols:
        if col in stocks_df.columns:
            stocks_df[col] = pd.to_numeric(stocks_df[col])
    
    # Add asset type
    stocks_df['asset_type'] = 'stock'
    
    # Get crypto positions
    try:
        my_crypto = rh.get_crypto_positions()
        crypto_data = {}
        
        for position in my_crypto:
            if float(position['quantity_available']) > 0:
                symbol = position['currency']['code']
                quantity = float(position['quantity_available'])
                
                # Get current price
                crypto_quote = rh.get_crypto_quote(symbol)
                price = float(crypto_quote['mark_price'])
                
                # Calculate values
                equity = price * quantity
                
                crypto_data[symbol] = {
                    'price': price,
                    'quantity': quantity,
                    'equity': equity,
                    'name': position['currency']['name'],
                    'asset_type': 'crypto'
                }
        
        # Convert to DataFrame
        if crypto_data:
            crypto_df = pd.DataFrame.from_dict(crypto_data, orient='index')
            
            # Combine stocks and crypto
            portfolio_df = pd.concat([stocks_df, crypto_df])
        else:
            portfolio_df = stocks_df
    except Exception as e:
        print(f"Error fetching crypto positions: {e}")
        portfolio_df = stocks_df
    
    return portfolio_df

def logout_from_robinhood():
    """
    Log out from Robinhood
    """
    rh.logout()
    print("Logged out from Robinhood")

if __name__ == "__main__":
    if login_to_robinhood():
        portfolio_df = get_portfolio_data()
        print("\nPortfolio Summary:")
        print(portfolio_df[['name', 'asset_type', 'quantity', 'price', 'equity']])
        logout_from_robinhood()