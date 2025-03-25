import os
import getpass
import time
from dotenv import load_dotenv
import robin_stocks.robinhood as rh
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import pickle

# Create cache directory if it doesn't exist
CACHE_DIR = Path(__file__).parent.parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)
PORTFOLIO_CACHE_FILE = CACHE_DIR / "portfolio_cache.pkl"

def _save_to_cache(data):
    """Save portfolio data and timestamp to cache"""
    cache_data = {
        'timestamp': datetime.now(),
        'data': data
    }
    with open(PORTFOLIO_CACHE_FILE, 'wb') as f:
        pickle.dump(cache_data, f)

def _load_from_cache():
    """Load portfolio data from cache if it exists and is less than 24 hours old"""
    if not PORTFOLIO_CACHE_FILE.exists():
        return None
        
    try:
        with open(PORTFOLIO_CACHE_FILE, 'rb') as f:
            cache_data = pickle.load(f)
            
        # Check if cache is less than 24 hours old
        if datetime.now() - cache_data['timestamp'] < timedelta(hours=24):
            return cache_data['data']
    except Exception as e:
        print(f"Error reading cache: {e}")
    return None

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

def get_portfolio_data(force_refresh=False):
    """
    Fetch portfolio data from Robinhood or cache
    Args:
        force_refresh (bool): If True, bypass cache and fetch fresh data
    """
    if not force_refresh:
        cached_data = _load_from_cache()
        if cached_data is not None:
            print("Using cached portfolio data (less than 24 hours old)")
            return cached_data

    try:
        my_stocks = rh.build_holdings()
        if not my_stocks:
            print("No stock positions found")
            return pd.DataFrame()
            
        # Convert to DataFrame for easier manipulation
        stocks_df = pd.DataFrame.from_dict(my_stocks, orient='index')
        
        # Convert numeric columns
        numeric_cols = ['price', 'quantity', 'average_buy_price', 'equity', 'percent_change', 'equity_change']
        for col in numeric_cols:
            if col in stocks_df.columns:
                stocks_df[col] = pd.to_numeric(stocks_df[col])
        
        portfolio_df = stocks_df
        
        # Save to cache
        _save_to_cache(portfolio_df)
        
        return portfolio_df
        
    except Exception as e:
        print(f"Error fetching portfolio data: {e}")
        return pd.DataFrame()

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