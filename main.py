import yfinance as yf
import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# ---------------------------
# 1. Download historical data
# ---------------------------
# Define tickers for multiple assets
tickers = {
    "S&P 500": "^GSPC",
    "Dow Jones": "^DJI",
    "NASDAQ": "^IXIC",
    "Gold": "GC=F",
    "Solana": "SOL-USD",
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD"
}

# Download historical price data starting from 2021-09-27
raw = yf.download(list(tickers.values()), start="2021-09-27", progress=False)

# If data has multiple levels of columns (Open, High, Low, Close, etc.), keep only 'Close'
if isinstance(raw.columns, pd.MultiIndex):
    data = raw['Close'].copy()
else:
    data = raw[['Close']].copy()

# Map ticker symbols back to readable names
symbol_to_name = dict(zip(list(tickers.values()), tickers.keys()))
data = data.rename(columns=symbol_to_name)

# Forward-fill missing values and drop columns that are completely empty
data = data.ffill().dropna(axis=1, how="all").sort_index()

# Prepare a list of dates for the range slider
date_list = data.index

# ---------------------------
# 2. Initialize Dash app and layout
# ---------------------------
app = Dash(__name__)

app.layout = html.Div(
    style={
        "height": "100vh",
        "display": "flex",
        "flexDirection": "column",
        "backgroundColor": "#111",
        "color": "white",
        "fontFamily": "Arial, sans-serif",
        "padding": "15px 30px"
    },
    children=[
        # Title
        html.H2(
            "📊 Multi-Asset Performance (Resets to Range Start)",
            style={"textAlign": "center", "marginBottom": "5px"}
        ),

        # Subtitle / instructions
        html.P(
            "Drag the range slider to select a time period — performance will reset to 0% at the new start date.",
            style={"textAlign": "center", "color": "#bbb", "marginBottom": "20px"}
        ),

        # Slider + live date display
        html.Div([
            html.Div(
                id='selected-range-display',
                style={
                    "textAlign": "center",
                    "fontSize": "18px",
                    "marginBottom": "12px",
                    "color": "white"
                }
            ),

            dcc.RangeSlider(
                id='date-range-slider',
                min=0,
                max=len(date_list) - 1,
                value=[0, len(date_list) - 1],
                allowCross=False,
                tooltip={"placement": "bottom", "always_visible": False},
                updatemode='drag',
                className="custom-range-slider"
            )
        ], style={"padding": "0 40px 25px 40px"}),

        # Graph to display asset performance
        dcc.Graph(id='performance-graph', style={"flex": "1"})
    ]
)

# ---------------------------
# 3. Callback to update graph and date display
# ---------------------------
@app.callback(
    [Output('performance-graph', 'figure'),
     Output('selected-range-display', 'children')],
    Input('date-range-slider', 'value')
)
def update_graph(selected_range):
    start_idx, end_idx = selected_range
    start_date = date_list[start_idx]
    end_date = date_list[end_idx]

    # Filter data for the selected range
    filtered = data.loc[start_date:end_date].copy()

    # Calculate performance relative to the first date in the range
    baseline = filtered.iloc[0]
    performance = (filtered / baseline - 1) * 100

    # Transform data into long format for Plotly Express
    df = performance.reset_index().melt(
        id_vars='Date',
        var_name='Asset',
        value_name='Performance (%)'
    )

    # Create the line chart
    fig = px.line(
        df,
        x='Date',
        y='Performance (%)',
        color='Asset',
        title=f"Performance from {start_date.date()}",
        labels={"Performance (%)": "Performance (%)", "Date": "Date"},
        template="plotly_dark"
    )

    # Format hover, y-axis, and add zero line
    fig.update_traces(hovertemplate='%{y:.2f}%<br>%{x|%Y-%m-%d}')
    fig.update_yaxes(ticksuffix="%")
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.update_layout(
        hovermode="x unified",
        legend_title_text="Assets",
        margin=dict(l=20, r=20, t=60, b=20)
    )

    # Display selected date range above slider
    range_text = html.Span([
        html.Span(start_date.strftime("%Y-%m-%d"), style={"color": "#1f77b4", "fontWeight": "bold"}),
        html.Span("  →  "),
        html.Span(end_date.strftime("%Y-%m-%d"), style={"color": "#1f77b4", "fontWeight": "bold"})
    ])

    return fig, range_text

# ---------------------------
# 4. Custom CSS for cleaner slider
# ---------------------------
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Performance Chart</title>
        {%favicon%}
        {%css%}
        <style>
            /* Customize slider track and handles */
            .rc-slider-track {
                background-color: #1f77b4 !important;
            }
            .rc-slider-handle {
                border: solid 2px #1f77b4 !important;
                background-color: white !important;
            }
            .rc-slider-dot-active {
                border-color: #1f77b4 !important;
            }
            /* Remove slider marks for cleaner look */
            .rc-slider-mark {
                display: none !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# ---------------------------
# 5. Run Dash app
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)



"""
import yfinance as yf
import plotly.express as px
import pandas as pd

# Define tickers
tickers = {
    "S&P 500": "^GSPC",
    "Dow Jones": "^DJI",
    "NASDAQ": "^IXIC",
    "Gold": "GC=F",
    "Solana": "SOL-USD",
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD"
}

# Download data
raw = yf.download(list(tickers.values()), start="2021-09-27", progress=False)

# Extract only 'Close' prices
if isinstance(raw.columns, pd.MultiIndex):
    data = raw['Close'].copy()
else:
    data = raw[['Close']].copy()

# Rename columns to readable asset names
symbol_to_name = dict(zip(list(tickers.values()), tickers.keys()))
data = data.rename(columns=symbol_to_name)

# Forward-fill missing prices
data = data.ffill()

# Drop columns with no data
data = data.dropna(axis=1, how="all")

# Normalize performance
base = data.apply(lambda col: col.loc[col.first_valid_index()] if col.first_valid_index() else None)
performance = (data / base - 1) * 100

# Reset index and melt
df = performance.reset_index().melt(id_vars="Date", var_name="Asset", value_name="Performance (%)")

# Plot with interactive enhancements
fig = px.line(
    df,
    x="Date",
    y="Performance (%)",
    color="Asset",
    title="Comparative Performance of Major Assets",
    labels={"Performance (%)": "Performance (%)", "Date": "Date"}
)

# Unified hover and better formatting
fig.update_traces(
    hovertemplate='<b>%{fullData.name}</b><br>%{x|%Y-%m-%d}<br>Performance: %{y:.2f}%'
)

# Add zero reference line
fig.add_hline(y=0, line_dash="dash", line_color="gray")

# Add range slider & selectors
fig.update_layout(
    hovermode="x unified",
    legend_title_text="Assets",
    template="plotly_dark",
    xaxis=dict(
        rangeslider=dict(visible=True),
        rangeselector=dict(
            bgcolor="#2a2a2a",  # dark background
            activecolor="#1f77b4",  # color for selected button
            bordercolor="#444",  # border for buttons
            font=dict(color="white"),  # button text color
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(count=3, label="3y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
)

fig.update_yaxes(ticksuffix="%")

# Save interactive chart to HTML
fig.write_html("performance_chart_interactive.html", include_plotlyjs="cdn", full_html=True)

print("Interactive chart saved as 'performance_chart_interactive.html'!")

fig.show()
"""