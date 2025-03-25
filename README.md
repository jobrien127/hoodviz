# HoodViz 📊

A powerful portfolio visualization tool for Robinhood accounts that helps you understand and analyze your investments through interactive charts and metrics.

## Features 🚀

- **Real-time Portfolio Data**: Fetches your current Robinhood portfolio data including stocks, ETPs, and cryptocurrencies
- **Data Caching**: Implements intelligent caching to minimize API calls (24-hour cache validity)
- **Multiple Visualization Types**:
  - 📈 Risk-Return Scatter Plot
  - 🥧 Portfolio Allocation Pie Chart
  - 🌳 Interactive Treemaps (Holdings & Performance)
  - 📊 Horizontal Bar Charts
  - 🌞 Asset Type Distribution (Sunburst)
  - 💧 Portfolio Weight Changes (Waterfall)
  - 🎯 Diversification Score Gauge
  - 🔄 ETP vs Stocks Comparison

## Installation 🛠️

NOTE: Due outstanding issues with robin_stocks. Changes have to be made to `venv/lib/python3.12/site-packages/robin_stocks/authentication.py` to successfullly authenticate with Robinhood.
This is an open issue on the robin_stocks repo.

1. Clone the repository:
```bash
git clone https://github.com/yourusername/hoodviz.git
cd hoodviz
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your Robinhood credentials:
```env
ROBINHOOD_USERNAME=your_email@example.com
ROBINHOOD_PASSWORD=your_password
```

## Usage 💻

1. Run the visualization tool:
```bash
python main.py
```

2. Optional flags:
   - `--force-refresh` or `-f`: Force refresh of portfolio data (bypass cache)
```bash
python main.py --force-refresh
```

3. The tool will:
   - Log in to your Robinhood account
   - Fetch your current portfolio data
   - Generate interactive visualizations
   - Save all visualizations in the `visualizations` folder

## Visualizations Explained 📈

1. **Risk-Return Scatter Plot**
   - X-axis: Return percentage
   - Y-axis: Portfolio weight
   - Point size: Position size
   - Color: Asset type
   - Helps identify best/worst performing positions relative to their weight

2. **Asset Type Distribution**
   - Sunburst chart showing portfolio allocation across different asset types
   - Interactive drilldown capability
   - Helps maintain desired asset allocation

3. **Portfolio Weight Changes**
   - Waterfall chart showing value changes by position
   - Helps track gainers and losers in absolute dollar terms
   - Useful for rebalancing decisions

4. **Diversification Score**
   - Gauge chart showing portfolio diversification (0-100)
   - Based on Herfindahl-Hirschman Index (HHI)
   - Green (66-100): Well diversified
   - Yellow (33-66): Moderately concentrated
   - Red (0-33): Highly concentrated

5. **Other Visualizations**
   - Treemaps for hierarchical portfolio view
   - Pie charts for simple portfolio allocation
   - Bar charts for detailed position analysis
   - ETP vs Stocks comparison

## File Structure 📁

```
hoodviz/
├── main.py              # Main script
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .env                # Credentials (create this)
├── cache/              # Data cache directory
├── src/               
│   ├── robinhood_client.py    # Robinhood API interface
│   └── portfolio_visualizer.py # Visualization logic
└── visualizations/     # Generated charts
```

## Dependencies 📚

- plotly: Interactive visualizations
- pandas: Data manipulation
- robin_stocks: Robinhood API client
- python-dotenv: Environment configuration
- matplotlib: Basic plotting support
- seaborn: Enhanced visualizations

## Notes 📝

- All visualizations are saved as interactive HTML files
- Crypto positions are handled with high precision (20 decimal places for now)
- Regular positions use standard precision (2 decimal places)
- Data is cached for 24 hours to minimize API calls
- Modern dark theme for all visualizations