import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
from pathlib import Path
import io

# Set dark style for matplotlib
plt.style.use('dark_background')
sns.set_style("darkgrid")

class PortfolioVisualizer:
    def __init__(self, portfolio_df):
        self.portfolio_df = portfolio_df
        self.output_dir = Path(__file__).parent.parent / "visualizations"
        self.output_dir.mkdir(exist_ok=True)
        
        # Set pandas display options to show all data
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        pd.set_option('display.expand_frame_repr', False)
        
        # Print DataFrame information
        print("\nPortfolio DataFrame:")
        print(self.portfolio_df.to_string())
        print("\nDataFrame Info:")
        print(self.portfolio_df.info())
        print("\nDetailed Description:")
        print(self.portfolio_df.describe(include='all').to_string())
        
        # Set dark theme configurations
        self.plotly_theme = "plotly_dark"
        self.color_scheme = px.colors.qualitative.Set3
        
        # Configure default layout settings for all visualizations
        self.default_layout = dict(
            paper_bgcolor='rgb(17, 17, 17)',  # Dark background for the chart container
            plot_bgcolor='rgb(17, 17, 17)',   # Dark background for the plot area
            font=dict(color='white'),         # White text
            title_font=dict(color='white'),   # White title text
            legend_font=dict(color='white'),  # White legend text
            xaxis=dict(
                gridcolor='rgba(128, 128, 128, 0.2)',  # Subtle grid
                zerolinecolor='rgba(128, 128, 128, 0.2)',
                color='white'  # White axis text
            ),
            yaxis=dict(
                gridcolor='rgba(128, 128, 128, 0.2)',  # Subtle grid
                zerolinecolor='rgba(128, 128, 128, 0.2)',
                color='white'  # White axis text
            )
        )
        
        # Ensure equity column is numeric
        if 'equity' in self.portfolio_df.columns:
            self.portfolio_df['equity'] = pd.to_numeric(self.portfolio_df['equity'])
            
        # Calculate portfolio percentages
        self.calculate_percentages()

    def calculate_percentages(self):
        """Calculate percentage of portfolio for each holding"""
        total_equity = self.portfolio_df['equity'].sum()
        self.portfolio_df['portfolio_percentage'] = (self.portfolio_df['equity'] / total_equity) * 100
        
    def update_chart_layout(self, fig, additional_settings=None):
        """Helper method to apply default layout settings and any additional settings"""
        settings = self.default_layout.copy()
        if additional_settings:
            settings.update(additional_settings)
        fig.update_layout(**settings)
        return fig

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
            
            if other_pct > 0:
                other_row = pd.DataFrame({
                    'equity': [small_holdings['equity'].sum()],
                    'portfolio_percentage': [other_pct],
                    'name': ['Other (< 1%)']
                })
                df = pd.concat([df, other_row])
        
        df = df.sort_values('portfolio_percentage', ascending=False)
        
        fig = px.pie(
            df, 
            values='portfolio_percentage', 
            names=df.index,
            title='Portfolio Allocation by Symbol',
            hover_data=['name', 'equity'],
            labels={'portfolio_percentage': 'Portfolio %'},
            template=self.plotly_theme,
            color_discrete_sequence=self.color_scheme
        )
        
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            textfont=dict(color='white')
        )
        self.update_chart_layout(fig, {
            'title_font_size': 24,
            'legend_title_font_size': 16,
            'legend_font_size': 12
        })
        
        output_path = self.output_dir / "portfolio_by_symbol.html"
        fig.write_html(str(output_path))
        print(f"Saved pie chart by symbol to {output_path}")
        fig.show()
        return fig

    def pie_chart_by_asset_type(self):
        """Create a pie chart of portfolio allocation by asset type"""
        df_by_type = self.portfolio_df.groupby('asset_type')['equity'].sum().reset_index()
        total = df_by_type['equity'].sum()
        df_by_type['percentage'] = (df_by_type['equity'] / total) * 100
        
        fig = px.pie(
            df_by_type, 
            values='equity', 
            names='asset_type',
            title='Portfolio Allocation by Asset Type',
            labels={'equity': 'Value ($)'},
            template=self.plotly_theme,
            color_discrete_sequence=self.color_scheme
        )
        
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            textfont=dict(color='white')
        )
        self.update_chart_layout(fig, {
            'title_font_size': 24
        })
        
        output_path = self.output_dir / "portfolio_by_asset_type.html"
        fig.write_html(str(output_path))
        print(f"Saved pie chart by asset type to {output_path}")
        fig.show()
        return fig

    def treemap_visualization(self):
        """Create a treemap visualization of portfolio holdings"""
        df = self.portfolio_df.copy()
        
        fig = px.treemap(
            df,
            path=[px.Constant("Portfolio"), 'asset_type', df.index],
            values='equity',
            color='portfolio_percentage',
            hover_data=['name', 'quantity', 'price'],
            color_continuous_scale='Viridis',
            title='Portfolio Treemap Visualization',
            template=self.plotly_theme
        )
        
        self.update_chart_layout(fig, {
            'title_font_size': 24
        })
        
        output_path = self.output_dir / "portfolio_treemap.html"
        fig.write_html(str(output_path))
        print(f"Saved treemap visualization to {output_path}")
        fig.show()
        return fig
    
    def bar_chart_top_holdings(self, top_n=10):
        """Create a bar chart of top N holdings"""
        df = self.portfolio_df.sort_values('equity', ascending=False).head(top_n)
        
        fig = px.bar(
            df,
            x=df.index,
            y='equity',
            color='asset_type',
            hover_data=['name', 'portfolio_percentage', 'quantity', 'price'],
            title=f'Top {top_n} Holdings by Value',
            template=self.plotly_theme,
            color_discrete_sequence=self.color_scheme
        )
        
        self.update_chart_layout(fig, {
            'title_font_size': 24,
            'xaxis_title': 'Symbol',
            'yaxis_title': 'Value ($)'
        })
        
        output_path = self.output_dir / f"top_{top_n}_holdings.html"
        fig.write_html(str(output_path))
        print(f"Saved top holdings bar chart to {output_path}")
        fig.show()
        return fig

    def sector_breakdown_large_cap(self):
        """Create a pie chart visualization of large cap holdings by sector"""
        df = self.portfolio_df.copy()
        large_cap_df = df[df['asset_type'] == 'Large Cap']
        df_by_sector = large_cap_df.groupby('sector')['equity'].sum().reset_index()
        total = df_by_sector['equity'].sum()
        df_by_sector['percentage'] = (df_by_sector['equity'] / total) * 100
        
        fig = px.pie(
            df_by_sector,
            values='equity',
            names='sector',
            title='Large Cap Holdings by Sector',
            labels={'equity': 'Value ($)'},
            hover_data=['percentage'],
            template=self.plotly_theme,
            color_discrete_sequence=self.color_scheme
        )
        
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            textfont=dict(color='white')
        )
        self.update_chart_layout(fig, {
            'title_font_size': 24,
            'legend_title_font_size': 16,
            'legend_font_size': 12
        })
        
        output_path = self.output_dir / "large_cap_by_sector.html"
        fig.write_html(str(output_path))
        print(f"Saved large cap sector breakdown to {output_path}")
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
            labels={'equity': 'Value ($)', 'index': 'Symbol'},
            template=self.plotly_theme,
            color_discrete_sequence=self.color_scheme
        )
        
        fig.update_layout(
            title_font_size=24,
            showlegend=True,
            xaxis_tickangle=-45,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        # Save interactive HTML
        output_path = self.output_dir / "miscellaneous_sector_holdings.html"
        fig.write_html(str(output_path))
        print(f"Saved miscellaneous sector holdings visualization to {output_path}")
        
        # Display the chart
        fig.show()
        
        return fig

    def portfolio_metrics_dashboard(self):
        """Create a comprehensive dashboard of portfolio metrics"""
        df = self.portfolio_df.copy()
        total_value = df['equity'].sum()
        
        # Calculate key metrics
        metrics = {
            'Total Portfolio Value': f'${total_value:,.2f}',
            'Number of Holdings': len(df),
            'Average Position Size': f'${(total_value / len(df)):,.2f}',
            'Largest Position': f'${df["equity"].max():,.2f}',
            'Smallest Position': f'${df["equity"].min():,.2f}'
        }
        
        # Asset type breakdown
        asset_type_values = df.groupby('asset_type')['equity'].sum()
        asset_type_pct = (asset_type_values / total_value * 100).round(2)
        
        # Sector exposure (for stocks only)
        stocks_df = df[df['asset_type'].isin(['Large Cap', 'Mid Cap', 'Small Cap'])]
        if not stocks_df.empty:
            sector_values = stocks_df.groupby('sector')['equity'].sum()
            sector_pct = (sector_values / stocks_df['equity'].sum() * 100).round(2)
        
        # Create the dashboard using plotly subplots
        fig = go.Figure()
        
        # Add metrics as a table with dark theme colors
        metrics_table = go.Table(
            header=dict(
                values=['Metric', 'Value'],
                fill_color='rgb(48, 48, 48)',
                align='left',
                font=dict(color='white', size=12)
            ),
            cells=dict(
                values=[list(metrics.keys()), list(metrics.values())],
                align='left',
                font=dict(color='white', size=12),
                fill_color='rgb(28, 28, 28)'
            )
        )
        
        # Create asset type donut chart
        asset_type_chart = go.Pie(
            values=asset_type_values,
            labels=asset_type_values.index,
            hole=0.4,
            name="Asset Types",
            domain=dict(x=[0, 0.45], y=[0.35, 0.8]),
            marker=dict(colors=self.color_scheme),
            textfont=dict(color='white')
        )
        
        # Add all traces
        fig.add_trace(metrics_table)
        fig.add_trace(asset_type_chart)
        
        # If we have stock sector data, add a sector breakdown chart
        if 'sector_values' in locals():
            sector_chart = go.Pie(
                values=sector_values,
                labels=sector_values.index,
                hole=0.4,
                name="Sector Exposure",
                domain=dict(x=[0.55, 1], y=[0.35, 0.8]),
                marker=dict(colors=self.color_scheme),
                textfont=dict(color='white')
            )
            fig.add_trace(sector_chart)
        
        # Update layout with dark theme
        self.update_chart_layout(fig, {
            'template': self.plotly_theme,
            'title': "Portfolio Metrics Dashboard",
            'title_x': 0.5,
            'title_font_size': 24,
            'showlegend': True,
            'height': 800,
            'annotations': [
                dict(text="Asset Type Distribution", x=0.225, y=25, showarrow=False, font_size=16, font_color='white'),
                dict(text="Sector Exposure (Stocks Only)", x=0.775, y=25, showarrow=False, font_size=16, font_color='white')
            ]
        })
        
        # Save interactive HTML
        output_path = self.output_dir / "portfolio_metrics_dashboard.html"
        fig.write_html(str(output_path))
        print(f"Saved portfolio metrics dashboard to {output_path}")
        
        # Display the chart
        fig.show()
        
        return fig