#!/usr/bin/env python3
"""
Robinhood Portfolio Visualization Tool
-------------------------------------
This script fetches your Robinhood portfolio data and creates
visualizations to help understand your asset diversification.
"""

import os
import sys
import argparse
from pathlib import Path
from src.robinhood_client import login_to_robinhood, get_portfolio_data, logout_from_robinhood
from src.portfolio_visualizer import PortfolioVisualizer

def main():
    """Main function to run the portfolio visualization tool"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Robinhood Portfolio Visualization Tool')
    parser.add_argument('--force-refresh', '-f', action='store_true',
                       help='Force refresh of portfolio data from Robinhood (bypass cache)')
    args = parser.parse_args()
    
    print("Robinhood Portfolio Visualization Tool")
    print("=====================================")
    
    # Login to Robinhood
    print("\nLogging in to Robinhood...")
    if not login_to_robinhood():
        return
    
    try:
        # Fetch portfolio data
        print("\nFetching your portfolio data...")
        portfolio_df = get_portfolio_data(force_refresh=args.force_refresh)
        
        if portfolio_df.empty:
            print("No portfolio data found. Make sure you have positions in your Robinhood account.")
            return
        
        print(f"\nSuccessfully retrieved {len(portfolio_df)} holdings")
        
        # Print portfolio summary
        total_value = portfolio_df['equity'].sum()
        print(f"\nTotal Portfolio Value: ${total_value:.2f}")
        print("\nTop 5 Holdings:")
        top_holdings = portfolio_df.sort_values('equity', ascending=False).head(5)
        for idx, row in top_holdings.iterrows():
            print(f"  {idx} ({row['name']}): ${row['equity']:.2f} ({(row['equity']/total_value)*100:.2f}%)")
        
        # Create visualizations
        print("\nGenerating visualizations...")
        visualizer = PortfolioVisualizer(portfolio_df)
        
        print("\n2. Creating pie chart by symbol...")
        visualizer.pie_chart_by_symbol()

        print("\n3. Creating etp vs stocks/adr...")
        visualizer.compare_etp_vs_stocks()
        
        print("\n4. Creating treemap visualization...")
        visualizer.treemap_visualization()

        print("\n5. Creating treemap performance visualization...")
        visualizer.treemap_perf_visualization()

        print("\n6. Creating bar chart by symbol...")
        visualizer.bar_chart_by_symbol()

        print("\n7. Creating risk-return scatter plot...")
        visualizer.risk_return_scatter()

        print("\n8. Creating asset type distribution...")
        visualizer.asset_type_distribution()

        print("\n9. Creating portfolio weight changes...")
        visualizer.portfolio_weight_changes()

        print("\n10. Creating diversification score...")
        visualizer.diversification_score()

        print("\nVisualizations complete! All charts have been saved to the 'visualizations' folder.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Logout from Robinhood
        logout_from_robinhood()

if __name__ == "__main__":
    main()