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
            # Get stock holdings
            my_stocks = rh.build_holdings()
            if not my_stocks:
                print("No stock positions found")
                stocks_df = pd.DataFrame()
            else:
                # Convert to DataFrame for easier manipulation
                stocks_df = pd.DataFrame.from_dict(my_stocks, orient='index')
                stocks_df['type'] = stocks_df['type'].fillna('stock')  # Ensure stock type is set
                
            # Get crypto holdings with high precision
            crypto_positions = rh.get_crypto_positions()
            crypto_holdings = {}
            
            if crypto_positions:  # Check if positions exist
                for position in crypto_positions:
                    try:
                        quantity = round(float(position.get('quantity', 0)), 20)
                        if quantity > 0:  # Only include non-zero positions
                            symbol = position.get('currency', {}).get('code')
                            if not symbol:
                                continue
                                
                            # Get current crypto price with high precision
                            quote = rh.get_crypto_quote(symbol)
                            if quote and isinstance(quote, dict):
                                price = round(float(quote.get('mark_price', 0)), 20)
                                equity = round(quantity * price, 20)
                                
                                cost_bases = position.get('cost_bases', [])
                                avg_cost = 0
                                if cost_bases and len(cost_bases) > 0:
                                    direct_cost = round(float(cost_bases[0].get('direct_cost_basis', 0)), 20)
                                    direct_quantity = round(float(cost_bases[0].get('direct_quantity', 1)), 20)
                                    if direct_quantity > 0:
                                        avg_cost = round(direct_cost / direct_quantity, 20)

                                print("Price:" , price, " Quantity:", quantity, " Equity:", equity, " Avg Cost:", avg_cost)

                                crypto_holdings[symbol] = {
                                    'price': price,
                                    'quantity': quantity,
                                    'equity': equity,
                                    'name': position.get('currency', {}).get('name', symbol),
                                    'type': 'crypto',
                                    'average_buy_price': avg_cost,
                                    'equity_change': round(equity - (quantity * avg_cost), 20)
                                }
                    except (TypeError, ValueError, KeyError) as e:
                        print(f"Error processing crypto position: {e}")
                        continue

            # Convert crypto to DataFrame
            if crypto_holdings:
                crypto_df = pd.DataFrame.from_dict(crypto_holdings, orient='index')
                # Combine stocks and crypto
                portfolio_df = pd.concat([stocks_df, crypto_df]) if not stocks_df.empty else crypto_df
            else:
                print("No crypto positions found")
                portfolio_df = stocks_df
                
            # Convert numeric columns - regular precision for stocks, high precision for crypto
            numeric_cols = ['price', 'quantity', 'average_buy_price', 'equity', 'percent_change', 'equity_change']
            for col in numeric_cols:
                if col in portfolio_df.columns:
                    # Convert to numeric first
                    portfolio_df[col] = pd.to_numeric(portfolio_df[col], errors='coerce')
                    # Round crypto values to 20 decimal places, others to 2
                    crypto_mask = portfolio_df['type'] == 'crypto'
                    portfolio_df.loc[crypto_mask, col] = portfolio_df.loc[crypto_mask, col].round(20)
                    portfolio_df.loc[~crypto_mask, col] = portfolio_df.loc[~crypto_mask, col].round(2)
            
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