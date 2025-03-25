import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import numpy as np

# Set dark style for matplotlib
plt.style.use('dark_background')
sns.set_style("darkgrid")

class PortfolioVisualizer:
    def __init__(self, portfolio_df):
        self.portfolio_df = portfolio_df
        self.output_dir = Path(__file__).parent.parent / "visualizations"
        self.output_dir.mkdir(exist_ok=True)

        # Display portfolio DataFrame
        pd.set_option('display.max_rows', None)  # Show all rows
        pd.set_option('display.max_columns', None)  # Show all columns
        pd.set_option('display.width', None)  # Don't wrap wide columns
        pd.set_option('display.float_format', lambda x: '%.5f' % x)  # Format floats to 20 decimal places
        
        print("\nDataFrame Information:")
        print("=" * 80)
        print("\nDataFrame Attributes:")
        print(f"Shape: {portfolio_df.shape}")
        print(f"Columns: {portfolio_df.columns.tolist()}")
        # print(f"Index: {portfolio_df.index.tolist()}")
        print(f"\nData Types:\n{portfolio_df.dtypes}")
        # print("\nSample Data:")
        # print(portfolio_df.head())
        # print("\nDataFrame Description:")
        # print(portfolio_df.describe())
        
        print("\nCurrent Portfolio Holdings:")
        print("=" * 80)
        print(portfolio_df)
        print("\nTotal Portfolio Value: ${:,.5f}".format(portfolio_df['equity'].sum()))
        
        # Set dark theme configurations
        self.plotly_theme = "plotly_dark"
        
        # Custom color sequence for pie charts (no white)
        self.pie_colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
            '#FFD93D', '#FF8C42', '#6C5B7B', '#C06C84',
            '#88D8B0', '#B5EAD7', '#E2F0CB', '#FFDAC1',
            '#9B7EDE', '#FF9A8B', '#98DDCA', '#D4A5A5'
        ]
        
        # Configure default layout settings for all visualizations
        self.default_layout = dict(
            paper_bgcolor='rgb(17, 17, 17)',  # Dark background
            plot_bgcolor='rgb(17, 17, 17)',   # Dark background
            font=dict(color='#808080'),       # Medium grey text
            title_font=dict(color='#808080'), # Medium grey title
            legend_font=dict(color='#808080'),# Medium grey legend
            xaxis=dict(
                gridcolor='rgba(128, 128, 128, 0.2)',
                zerolinecolor='rgba(128, 128, 128, 0.2)',
                color='#808080'  # Medium grey axis text
            ),
            yaxis=dict(
                gridcolor='rgba(128, 128, 128, 0.2)',
                zerolinecolor='rgba(128, 128, 128, 0.2)',
                color='#808080'  # Medium grey axis text
            )
        )
        
        # Ensure equity column is numeric with appropriate precision
        if 'equity' in self.portfolio_df.columns:
            self.portfolio_df['equity'] = pd.to_numeric(self.portfolio_df['equity'])
            # Apply precision based on type
            crypto_mask = self.portfolio_df['type'] == 'crypto'
            self.portfolio_df.loc[crypto_mask, 'equity'] = self.portfolio_df.loc[crypto_mask, 'equity'].round(20)
            self.portfolio_df.loc[~crypto_mask, 'equity'] = self.portfolio_df.loc[~crypto_mask, 'equity'].round(2)
            
        # Calculate portfolio percentages
        self.calculate_percentages()

    def calculate_percentages(self):
        """Calculate percentage of portfolio for each holding"""
        total_equity = self.portfolio_df['equity'].sum().round(2)  # Total always in 2 decimals
        self.portfolio_df['portfolio_percentage'] = (self.portfolio_df['equity'] / total_equity * 100)
        # Round percentages based on asset type
        crypto_mask = self.portfolio_df['type'] == 'crypto'
        self.portfolio_df.loc[crypto_mask, 'portfolio_percentage'] = self.portfolio_df.loc[crypto_mask, 'portfolio_percentage'].round(20)
        self.portfolio_df.loc[~crypto_mask, 'portfolio_percentage'] = self.portfolio_df.loc[~crypto_mask, 'portfolio_percentage'].round(2)

    def update_chart_layout(self, fig, additional_settings=None):
        """Helper method to apply default layout settings and any additional settings"""
        settings = self.default_layout.copy()
        if additional_settings:
            settings.update(additional_settings)
        fig.update_layout(**settings)
        return fig

    def pie_chart_by_symbol(self, min_percentage=0.0):
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
            color_discrete_sequence=self.pie_colors  # Use our custom colors
        )
        
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            textfont=dict(color='#000000')  # Medium grey text
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

    def treemap_visualization(self):
        """Create a treemap visualization of portfolio holdings"""
        df = self.portfolio_df.copy()
        
        # Handle crypto assets and combine stocks/ADRs
        df.loc[df['type'].isin(['stock', 'adr']), 'type'] = 'stocks'  # Combine stocks and ADRs
        
        fig = px.treemap(
            df,
            path=[px.Constant("Portfolio"), 'type', df.index],
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
    
    def treemap_perf_visualization(self):
        """Create a treemap visualization of portfolio holdings and performance"""
        df = self.portfolio_df.copy()
        
        # Handle crypto assets and combine stocks/ADRs
        df.loc[df['type'].isin(['stock', 'adr']), 'type'] = 'stocks'  # Combine stocks and ADRs
        
        # Normalize equity_change to [-1, 1] range for better visualization
        if not df['equity_change'].empty:
            max_abs_change = abs(df['equity_change']).max()
            if max_abs_change != 0:  # Avoid division by zero
                df['normalized_change'] = df['equity_change'] / max_abs_change
            else:
                df['normalized_change'] = df['equity_change']
        else:
            df['normalized_change'] = 0
            
        # Store original values for hover display
        df['equity_change_display'] = df['equity_change'].apply(lambda x: f'${x:,.2f}')
        df['portfolio_percentage_display'] = df['portfolio_percentage'].apply(lambda x: f'{x:.5f}%')
        
        fig = px.treemap(
            df,
            path=[px.Constant("Portfolio"), 'type', df.index],
            values='equity',        
            color='normalized_change',
            hover_data={
                'name': True,
                'quantity': ':.8f',
                'price': ':.2f',
                'equity_change_display': True,
                'portfolio_percentage_display': True
            },
            color_continuous_scale=[(0, "red"), (0.5, "white"), (1, "green")],
            color_continuous_midpoint=0,  # Center the color scale at 0
            title='Portfolio Performance Treemap',
            template=self.plotly_theme
        )
        
        # Update hover template to show actual equity change and portfolio percentage
        fig.update_traces(
            hovertemplate="<b>%{label}</b><br>" +
                         "Type: %{parent}<br>" +
                         "Name: %{customdata[0]}<br>" +
                         "Quantity: %{customdata[1]}<br>" +
                         "Price: $%{customdata[2]}<br>" +
                         "Change: %{customdata[3]}<br>" +
                         "Portfolio %: %{customdata[4]}<br>" +
                         "<extra></extra>"
        )
        
        self.update_chart_layout(fig, {
            'title_font_size': 24,
            'coloraxis_colorbar_title': 'Relative Performance'
        })
        
        output_path = self.output_dir / "portfolio_treemap.html"
        fig.write_html(str(output_path))
        print(f"Saved performance treemap visualization to {output_path}")
        fig.show()
        return fig

    def compare_etp_vs_stocks(self):
        """Create side-by-side pie charts comparing ETPs vs Stocks/ADRs"""
        df = self.portfolio_df.copy()
        
        # Filter out crypto (NaN types) and separate ETPs from Stocks/ADRs
        df = df.dropna(subset=['type'])
        etp_df = df[df['type'] == 'etp']
        stocks_df = df[df['type'].isin(['stock', 'adr'])]
        
        # Create subplots for the two pie charts
        fig = go.Figure()
        
        # ETP Chart
        etp_by_symbol = etp_df.groupby(etp_df.index)['equity'].sum()
        etp_total = etp_by_symbol.sum()
        
        fig.add_trace(go.Pie(
            values=etp_by_symbol,
            labels=etp_by_symbol.index,
            name="ETPs",
            domain=dict(x=[0, 0.45]),
            title="ETP Allocation",
            textfont=dict(color='#000000'),  # Medium grey text
            hole=0.3,
            marker=dict(colors=self.pie_colors)  # Use our custom colors
        ))
        
        # Stocks/ADRs Chart
        stocks_by_symbol = stocks_df.groupby(stocks_df.index)['equity'].sum()
        stocks_total = stocks_by_symbol.sum()
        
        fig.add_trace(go.Pie(
            values=stocks_by_symbol,
            labels=stocks_by_symbol.index,
            name="Stocks/ADRs",
            domain=dict(x=[0.55, 1]),
            title="Stocks/ADRs Allocation",
            textfont=dict(color='#000000'),  # Medium grey text
            hole=0.3,
            marker=dict(colors=self.pie_colors)  # Use our custom colors
        ))
        
        # Update layout with annotations
        self.update_chart_layout(fig, {
            'title': 'ETPs vs Stocks/ADRs Comparison',
            'title_x': 0.5,
            'title_font_size': 24,
            'showlegend': True,
            'height': 1200,
            'annotations': [
                dict(
                    text=f'Total ETP Value: ${etp_total:.2f}',
                    x=0.225, y=-0.1,
                    showarrow=False,
                    font_size=14,
                    font_color='#808080'
                ),
                dict(
                    text=f'Total Stocks/ADRs Value: ${stocks_total:.2f}',
                    x=0.775, y=-0.1,
                    showarrow=False,
                    font_size=14,
                    font_color='#808080'
                )
            ]
        })
        
        # Save interactive HTML
        output_path = self.output_dir / "etp_vs_stocks_comparison.html"
        fig.write_html(str(output_path))
        print(f"Saved ETP vs Stocks comparison to {output_path}")
        
        # Display the chart
        fig.show()
        
        return fig

    def bar_chart_by_symbol(self, min_percentage=0.0):
        """
        Create a bar chart of portfolio allocation by symbol
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
        
        df = df.sort_values('portfolio_percentage', ascending=True)  # Sort ascending for better visualization
        
        fig = go.Figure(data=[
            go.Bar(
                x=df['portfolio_percentage'],
                y=df.index,
                orientation='h',
                text=[f'{pct:.2f}%' for pct in df['portfolio_percentage']],
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>' +
                             'Portfolio %: %{x:.2f}%<br>' +
                             'Equity: $%{customdata[0]:,.2f}<br>' +
                             'Name: %{customdata[1]}<extra></extra>',
                customdata=df[['equity', 'name']].values,
                marker=dict(color=self.pie_colors[0])  # Use first color from our palette
            )
        ])
        
        # Update layout for better readability
        self.update_chart_layout(fig, {
            'title': 'Portfolio Allocation by Symbol',
            'title_font_size': 24,
            'height': max(600, len(df) * 25),  # Dynamic height based on number of symbols
            'xaxis_title': 'Portfolio Percentage',
            'yaxis_title': 'Symbol',
            'yaxis': {'categoryorder': 'total ascending'},  # Sort bars by value
            'margin': dict(l=20, r=20, t=40, b=20),
            'bargap': 0.15
        })
        
        output_path = self.output_dir / "portfolio_by_symbol_bar.html"
        fig.write_html(str(output_path))
        print(f"Saved bar chart by symbol to {output_path}")
        fig.show()
        return fig

    def risk_return_scatter(self):
        """Create a scatter plot showing risk vs return for each holding"""
        df = self.portfolio_df.copy()
        
        fig = px.scatter(
            df,
            x='percent_change',
            y='portfolio_percentage',
            text=df.index,
            color='type',
            size='equity',
            title='Risk-Return Analysis',
            labels={
                'percent_change': 'Return (%)',
                'portfolio_percentage': 'Portfolio Weight (%)',
                'type': 'Asset Type'
            },
            template=self.plotly_theme
        )
        
        self.update_chart_layout(fig, {
            'title_font_size': 24,
            'xaxis_title': 'Return (%)',
            'yaxis_title': 'Portfolio Weight (%)'
        })
        
        output_path = self.output_dir / "risk_return_scatter.html"
        fig.write_html(str(output_path))
        print(f"Saved risk-return scatter plot to {output_path}")
        fig.show()
        return fig

    def asset_type_distribution(self):
        """Create a sunburst chart showing distribution across asset types"""
        df = self.portfolio_df.copy()
        
        # Calculate total value per asset type
        type_totals = df.groupby('type')['equity'].sum().reset_index()
        
        fig = px.sunburst(
            type_totals,
            path=['type'],
            values='equity',
            title='Asset Type Distribution',
            template=self.plotly_theme,
            color_discrete_sequence=self.pie_colors
        )
        
        self.update_chart_layout(fig, {
            'title_font_size': 24
        })
        
        output_path = self.output_dir / "asset_type_distribution.html"
        fig.write_html(str(output_path))
        print(f"Saved asset type distribution to {output_path}")
        fig.show()
        return fig

    def portfolio_weight_changes(self):
        """Create a waterfall chart showing how portfolio weights have changed"""
        df = self.portfolio_df.copy()
        
        fig = go.Figure(go.Waterfall(
            name="Portfolio Changes",
            orientation="v",
            measure=["relative"] * len(df),
            x=df.index,
            textposition="outside",
            text=[f"{x:+.2f}%" for x in df['percent_change']],
            y=df['equity_change'],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))
        
        self.update_chart_layout(fig, {
            'title': 'Portfolio Weight Changes',
            'title_font_size': 24,
            'showlegend': False,
            'xaxis_title': 'Holdings',
            'yaxis_title': 'Change in Value ($)'
        })
        
        output_path = self.output_dir / "portfolio_weight_changes.html"
        fig.write_html(str(output_path))
        print(f"Saved portfolio weight changes to {output_path}")
        fig.show()
        return fig

    def diversification_score(self):
        """Create a gauge chart showing portfolio diversification score"""
        df = self.portfolio_df.copy()
        
        # Calculate Herfindahl-Hirschman Index (HHI)
        weights = df['portfolio_percentage'] / 100
        hhi = (weights ** 2).sum()
        # Convert to diversification score (0-100, higher is better)
        div_score = max(0, min(100, (1 - hhi) * 100))
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=div_score,
            title={'text': "Diversification Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': self.pie_colors[0]},
                'steps': [
                    {'range': [0, 33], 'color': 'red'},
                    {'range': [33, 66], 'color': 'yellow'},
                    {'range': [66, 100], 'color': 'green'}
                ]
            }
        ))
        
        self.update_chart_layout(fig, {
            'title_font_size': 24
        })
        
        output_path = self.output_dir / "diversification_score.html"
        fig.write_html(str(output_path))
        print(f"Saved diversification score to {output_path}")
        fig.show()
        return fig