import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from Backtest.Technicals.Basic import *
import math

# Function to create a candlestick trace
def create_candlestick_trace(df):
    return go.Candlestick(
        x=df["Date"],
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="OHLC",
        increasing_line_color="green",  # Up days (green)
        decreasing_line_color="red",  # Down days (red)
    )

# Function to create overlay indicators (e.g., SMA, Bollinger Bands)
def create_overlay_indicators_traces(df, overlay_indicators):
    traces = []
    for indicator_func in overlay_indicators:
        indicator_data = indicator_func(df)
        for i, data in enumerate(indicator_data[1:], start=1):
            trace = go.Scatter(
                x=indicator_data[0],  # x values (dates)
                y=data,  # y values (one of the outputs)
                mode="lines",
                name=f"{indicator_func.__name__} {i}",  # Unique name for each trace
                line=dict(width=2)
            )
            traces.append(trace)
    return traces

# Function to create volume bar chart
def create_volume_trace(df):
    return go.Bar(
        x=df["Date"],
        y=df["Volume"],
        name="Volume",
        marker=dict(color="#ff7f0e")
    )

# Function to create below indicators (e.g., RSI, MACD)
def create_below_indicators_traces(df, indicators_below):
    traces = []
    for i, indicator_func in enumerate(indicators_below, start=2):  # Start adding from row 2
        indicator_data = indicator_func(df)
        trace = go.Scatter(
            x=indicator_data[0],  # x values (dates)
            y=indicator_data[1],  # y values (indicator values)
            mode="lines",
            name=indicator_func.__name__,  # Use the function name as the trace name
            line=dict(width=2)
        )
        traces.append(trace)
    return traces

# Function to create buttons for toggling visibility of traces
def create_visibility_buttons(all_traces):
    buttons = [
        {'label': 'Show All', 'method': 'update', 'args': [{'visible': [True] * len(all_traces)}, {'title': 'All Indicators Displayed'}]}
    ]

    for idx, trace_name in enumerate(all_traces, 1):
        visible_list = [True] * len(all_traces)  # Start with everything visible
        visible_list[idx - 1] = False  # Hide current trace
        buttons.append({
            'label': f'Hide {trace_name}',
            'method': 'update',
            'args': [{'visible': visible_list}, {'title': f'{trace_name} Only'}]
        })

    buttons.append({
        'label': 'Show None',
        'method': 'update',
        'args': [{'visible': [True] + [False] * (len(all_traces) - 1)}, {'title': 'Candlestick Only'}]
    })

    return buttons

# Function to update the layout of the figure
def update_layout(fig, all_traces):
    fig.update_layout(
        title=f"Stock Candlestick Chart with Technical Indicators",
        template="plotly_dark",  # Dark Bloomberg-style theme
        showlegend=True,  # Show legend for indicators
        xaxis=dict(title="Date", showgrid=True, tickformat="%b %d", rangeslider=dict(visible=False)),
        yaxis=dict(title="Price", showgrid=True),
        yaxis2=dict(title="Technical Indicator", showgrid=True),
        yaxis3=dict(title="Volume", showgrid=True),
        height=900,
        updatemenus=[
            {
                'buttons': create_visibility_buttons(all_traces),
                'direction': 'down',
                'showactive': True,
                'x': 1,  # Positioning on x-axis
                'xanchor': 'right',
                'y': 1.15,  # Positioning on y-axis
                'yanchor': 'top'
            }
        ]
    )

# Main function to plot the stock with technical indicators
def plot_stock(ticker_symbol, period='10y', overlay_indicators=[], indicators_below=[]):
    # Download historical data for the specified ticker symbol
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period=period).reset_index()

    # Determine the number of subplots required based on the number of below indicators
    num_rows = 2 + len(indicators_below)  # 2 subplots (Candlestick & Volume) + below indicator subplots

    # Create figure with dynamic number of subplots
    fig = make_subplots(
        rows=num_rows,
        cols=1,
        shared_xaxes=True,  # This ensures the x-axis is shared between all plots
        vertical_spacing=0.1,  # Adjusts spacing between subplots
        row_heights=[0.7] + (num_rows - 1) * [0.2]  # Default equal height for all except volume
    )

    # Add Candlestick trace (first subplot)
    fig.add_trace(create_candlestick_trace(df), row=1, col=1)

    # Add Overlay Indicators (on stock price)
    overlay_traces = create_overlay_indicators_traces(df, overlay_indicators)
    for trace in overlay_traces:
        fig.add_trace(trace, row=1, col=1)  # Overlay on the first subplot (stock price)

    # Add Volume Bar Chart (last subplot)
    fig.add_trace(create_volume_trace(df), row=num_rows, col=1)

    # Add Indicators Below (e.g., RSI, MACD)
    below_traces = create_below_indicators_traces(df, indicators_below)
    for i, trace in enumerate(below_traces, start=2):  # Start adding from row 2
        fig.add_trace(trace, row=i, col=1)

    # Create a list of all trace names for the buttons
    all_traces = ['Candlestick'] + [trace['name'] for trace in overlay_traces] + [trace['name'] for trace in below_traces]

    # Update layout with the visibility buttons
    update_layout(fig, all_traces)

    # Show the figure
    return fig

def plot_multiple_stocks(ticker_symbols, period='10y', overlay_indicators=[], indicators_below=[]):
    # Calculate the number of rows needed based on the number of stocks and a maximum of 3 columns per row
    num_stocks = len(ticker_symbols)
    num_columns = 3  # Maximum 3 columns per row
    num_rows = math.ceil(num_stocks / num_columns)*2  # Calculate rows needed
    row_heights = [0.8, 0.2] * num_stocks  # Alternating 0.8 and 0.2 for each stock's rows


    # Create an empty main figure
    fig = make_subplots(
        rows=num_rows,
        cols=num_columns,
        shared_xaxes=True,  # Share the x-axis for all subplots
        vertical_spacing=0.1,  # Adjust vertical spacing
        subplot_titles=ticker_symbols  # Add the stock symbols as subplot titles
    )

    # Loop through the list of ticker symbols and call the plot_stock function for each
    for idx, stock in enumerate(ticker_symbols):
        row = (idx // num_columns) + 1  # Determine row based on stock index
        col = (idx % num_columns) + 1  # Determine column based on stock index

        # Call the plot_stock function for each stock, and get the figure returned
        stock_fig = plot_stock(stock, period=period, overlay_indicators=overlay_indicators,
                               indicators_below=indicators_below)

        # Loop through each trace in the returned stock figure and add it to the main fig
        for trace in stock_fig['data']:
            if trace['name'] == 'OHLC':  # Main stock price plot
                fig.add_trace(trace, row=row, col=col)
            elif trace['name'] == 'Volume':  # Volume plot
                # Place volume trace on a separate subplot (below main plot)
                fig.add_trace(trace, row=row + 1, col=col)
            else:  # Add other overlays and indicators as needed
                # Place overlay and indicator traces in the main plot
                fig.add_trace(trace, row=row, col=col)

    # Layout formatting (adjusts title, x-axis, etc.)
    fig.update_layout(
        title="Multiple Stocks Candlestick Chart with Technical Indicators",
        template="plotly_dark",  # Dark theme
        showlegend=True,  # Show legend for indicators
        xaxis=dict(title="Date", showgrid=True, tickformat="%b %d", rangeslider=dict(visible=False)),
        yaxis=dict(title="Price", showgrid=True),  # Shared y-axis for all subplots
        height=900,
        row_heights=row_heights
    )

    # Show the figure
    fig.show()

tickers = ["JPM", "BAC", "V", "GS", "C"]
plot_stock("JPM", period='4y', overlay_indicators=[bollinger_bands], indicators_below=[ema, sma]).show()
# plot_multiple_stocks(tickers, period='4y', overlay_indicators=[], indicators_below=[])