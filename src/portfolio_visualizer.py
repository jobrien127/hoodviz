import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
from pathlib import Path

# Set style for matplotlib
sns.set_style("whitegrid")

class PortfolioVisualizer:
    def __init__(self, portfolio_df):
        self.portfolio_df = portfolio_df
        self.output_dir = Path(__file__).parent.parent / "visualizations"
        self.output_dir.mkdir(exist_ok=True)
        
        # Ensure equity column is numeric
        if 'equity' in self.portfolio_df.columns:
            self.portfolio_df['equity'] = pd.to_numeric(self.portfolio_df['equity'])
            
        # Calculate portfolio percentages
        self.calculate_percentages()
    
    def calculate_percentages(self):
        """Calculate percentage of portfolio for each holding"""
        total_equity = self.portfolio_df['equity'].sum()
        self.portfolio_df['portfolio_percentage'] = (self.portfolio_df['equity'] / total_equity) * 100
        
    def pie_chart_by_symbol(self, min_percentage=1.0):
        """
        Create a pie chart of portfolio allocation by symbol
        Holdings below min_percentage will be grouped as 'Other'
        """
        df = self.portfolio_df.copy()
        
        # Group small holdings
        small_holdings = df[df['portfolio_percentage'] < min_percentage]
        if not small_holdings.empty:
            other_pct = small_holdings['portfolio_percentage'].sum()
            df = df[df['portfolio_percentage'] >= min_percentage]
            
            # Add 'Other' category if there are small holdings
            if other_pct > 0:
                other_row = pd.DataFrame({
                    'equity': [small_holdings['equity'].sum()],
                    'portfolio_percentage': [other_pct],
                    'name': ['Other (< 1%)']
                })
                df = pd.concat([df, other_row])
        
        # Sort by percentage (descending)
        df = df.sort_values('portfolio_percentage', ascending=False)
        
        # Create and save pie chart using Plotly
        fig = px.pie(
            df, 
            values='portfolio_percentage', 
            names=df.index,
            title='Portfolio Allocation by Symbol',
            hover_data=['name', 'equity'],
            labels={'portfolio_percentage': 'Portfolio %'}
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            title_font_size=24,
            legend_title_font_size=16,
            legend_font_size=12
        )
        
        # Save interactive HTML
        output_path = self.output_dir / "portfolio_by_symbol.html"
        fig.write_html(str(output_path))
        print(f"Saved pie chart by symbol to {output_path}")
        
        # Display the chart
        fig.show()
        
        return fig
        
    def pie_chart_by_asset_type(self):
        """Create a pie chart of portfolio allocation by asset type"""
        # Group by asset type and sum equity
        df_by_type = self.portfolio_df.groupby('asset_type')['equity'].sum().reset_index()
        total = df_by_type['equity'].sum()
        df_by_type['percentage'] = (df_by_type['equity'] / total) * 100
        
        # Create and save pie chart using Plotly
        fig = px.pie(
            df_by_type, 
            values='equity', 
            names='asset_type',
            title='Portfolio Allocation by Asset Type',
            labels={'equity': 'Value ($)'}
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            title_font_size=24
        )
        
        # Save interactive HTML
        output_path = self.output_dir / "portfolio_by_asset_type.html"
        fig.write_html(str(output_path))
        print(f"Saved pie chart by asset type to {output_path}")
        
        # Display the chart
        fig.show()
        
        return fig
        
    def treemap_visualization(self):
        """Create a treemap visualization of portfolio holdings"""
        df = self.portfolio_df.copy()
        
        # Create and save treemap using Plotly
        fig = px.treemap(
            df,
            path=[px.Constant("Portfolio"), 'asset_type', df.index],
            values='equity',
            color='portfolio_percentage',
            hover_data=['name', 'quantity', 'price'],
            color_continuous_scale='RdBu',
            title='Portfolio Treemap Visualization'
        )
        
        fig.update_layout(
            title_font_size=24
        )
        
        # Save interactive HTML
        output_path = self.output_dir / "portfolio_treemap.html"
        fig.write_html(str(output_path))
        print(f"Saved treemap visualization to {output_path}")
        
        # Display the chart
        fig.show()
        
        return fig
    
    def bar_chart_top_holdings(self, top_n=10):
        """Create a bar chart of top N holdings"""
        # Sort and get top N holdings
        df = self.portfolio_df.sort_values('equity', ascending=False).head(top_n)
        
        # Create and save bar chart using Plotly
        fig = px.bar(
            df,
            x=df.index,
            y='equity',
            color='asset_type',
            hover_data=['name', 'portfolio_percentage', 'quantity', 'price'],
            title=f'Top {top_n} Holdings by Value'
        )
        
        fig.update_layout(
            xaxis_title='Symbol',
            yaxis_title='Value ($)',
            title_font_size=24
        )
        
        # Save interactive HTML
        output_path = self.output_dir / f"top_{top_n}_holdings.html"
        fig.write_html(str(output_path))
        print(f"Saved top holdings bar chart to {output_path}")
        
        # Display the chart
        fig.show()
        
        return fig

    def sector_breakdown_large_cap(self):
        """Create a pie chart visualization of large cap holdings by sector"""
        # Filter for large cap holdings and group by sector
        df = self.portfolio_df.copy()
        large_cap_df = df[df['asset_type'] == 'Large Cap']
        df_by_sector = large_cap_df.groupby('sector')['equity'].sum().reset_index()
        total = df_by_sector['equity'].sum()
        df_by_sector['percentage'] = (df_by_sector['equity'] / total) * 100
        
        # Create and save pie chart using Plotly
        fig = px.pie(
            df_by_sector,
            values='equity',
            names='sector',
            title='Large Cap Holdings by Sector',
            labels={'equity': 'Value ($)'},
            hover_data=['percentage']
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            title_font_size=24,
            legend_title_font_size=16,
            legend_font_size=12
        )
        
        # Save interactive HTML
        output_path = self.output_dir / "large_cap_by_sector.html"
        fig.write_html(str(output_path))
        print(f"Saved large cap sector breakdown to {output_path}")
        
        # Display the chart
        fig.show()
        
        return fig

    def display_miscellaneous_stocks(self):
        """Create a visualization for stocks categorized in the Miscellaneous sector"""
        df = self.portfolio_df.copy()
        
        # Filter for stocks in Miscellaneous sector
        misc_stocks = df[df['sector'] == 'Miscellaneous']
        
        if misc_stocks.empty:
            print("No stocks found in Miscellaneous sector")
            return None
            
        # Sort by equity value
        misc_stocks = misc_stocks.sort_values('equity', ascending=False)
        
        # Create bar chart
        fig = px.bar(
            misc_stocks,
            x=misc_stocks.index,
            y='equity',
            title='Miscellaneous Sector Holdings',
            hover_data=['name', 'portfolio_percentage', 'quantity', 'price', 'asset_type'],
            labels={'equity': 'Value ($)', 'index': 'Symbol'}
        )
        
        fig.update_layout(
            title_font_size=24,
            showlegend=True,
            xaxis_tickangle=-45
        )
        
        # Save interactive HTML
        output_path = self.output_dir / "miscellaneous_sector_holdings.html"
        fig.write_html(str(output_path))
        print(f"Saved miscellaneous sector holdings visualization to {output_path}")
        
        # Display the chart
        fig.show()
        
        # Print detailed information
        print("\nDetailed Miscellaneous Sector Holdings:")
        print("=====================================")
        for symbol, row in misc_stocks.iterrows():
            print(f"{symbol} ({row['name']}):")
            print(f"  Value: ${row['equity']:.2f}")
            print(f"  Quantity: {row['quantity']}")
            print(f"  Current Price: ${row['price']:.2f}")
            print(f"  Portfolio %: {row['portfolio_percentage']:.2f}%")
            print("-------------------------------------")
        
        return fig