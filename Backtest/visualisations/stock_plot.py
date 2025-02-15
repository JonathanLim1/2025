import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Define technical indicators functions (e.g., RSI, SMA, EMA)
def sma(df, window=50):
    sma_values = df["Close"].rolling(window=window).mean()
    return df["Date"], sma_values

def rsi(df, window=14):
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-10)
    rsi_values = 100 - (100 / (1 + rs))
    return df["Date"], rsi_values

# Fetch stock data
ticker = yf.Ticker("AAPL")
df = ticker.history(period='1y').reset_index()

# Create figure with one subplot for candlestick chart
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.7, 0.3])

# Add Candlestick trace
fig.add_trace(
    go.Candlestick(
        x=df["Date"],
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="OHLC",
        increasing_line_color="green",  # Up days (green)
        decreasing_line_color="red"     # Down days (red)
    ),
    row=1, col=1
)

# Add SMA and RSI indicators
sma_dates, sma_values = sma(df)
fig.add_trace(
    go.Scatter(x=sma_dates, y=sma_values, mode="lines", name="SMA", line=dict(width=2)),
    row=1, col=1
)

rsi_dates, rsi_values = rsi(df)
fig.add_trace(
    go.Scatter(x=rsi_dates, y=rsi_values, mode="lines", name="RSI", line=dict(width=2)),
    row=2, col=1
)

# Dropdown menu for selecting indicators
fig.update_layout(
    title="Candlestick Chart with Technical Indicators",
    template="plotly_dark",
    xaxis=dict(title="Date", showgrid=True, tickformat="%b %d"),
    yaxis=dict(title="Price", showgrid=True),
    height=600,
    updatemenus=[
        {
            'buttons': [
                {'label': 'Show All', 'method': 'update', 'args': [{'visible': [True, True, True]}, {'title': 'All Indicators Displayed'}]},
                {'label': 'Hide SMA', 'method': 'update', 'args': [{'visible': [True, False, True]}, {'title': 'RSI Only'}]},
                {'label': 'Hide RSI', 'method': 'update', 'args': [{'visible': [True, True, False]}, {'title': 'SMA Only'}]},
                {'label': 'Show None', 'method': 'update', 'args': [{'visible': [True, False, False]}, {'title': 'Candlestick Only'}]},
            ],
            'direction': 'down',
            'showactive': True,
            'x': 0.1,  # Positioning on x-axis
            'xanchor': 'left',
            'y': 1.15,  # Positioning on y-axis
            'yanchor': 'top'
        }
    ]
)

fig.show()
