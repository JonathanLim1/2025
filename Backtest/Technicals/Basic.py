import pandas as pd

# 1. Simple Moving Average (SMA)
def sma(df, window=50):
    sma_values = df["Close"].rolling(window=window).mean()
    return df["Date"], sma_values

# 2. Exponential Moving Average (EMA)
def ema(df, window=50):
    ema_values = df["Close"].ewm(span=window, adjust=False).mean()
    return df["Date"], ema_values

# 3. Relative Strength Index (RSI)
def rsi(df, window=14):
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi_values = 100 - (100 / (1 + rs))
    return df["Date"], rsi_values

# 4. Bollinger Bands (BB)
def bollinger_bands(df, window=20, num_std=2):
    ma = df["Close"].rolling(window=window).mean()
    stddev = df["Close"].rolling(window=window).std()
    upper_band = ma + num_std * stddev
    lower_band = ma - num_std * stddev
    return df["Date"], upper_band, lower_band

# 5. Moving Average Convergence Divergence (MACD)
def macd(df, short_window=12, long_window=26, signal_window=9):
    short_ema = df["Close"].ewm(span=short_window, adjust=False).mean()
    long_ema = df["Close"].ewm(span=long_window, adjust=False).mean()
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    histogram = macd_line - signal_line
    return df["Date"], macd_line, signal_line, histogram

# 6. Average True Range (ATR)
def atr(df, window=14):
    df['H-L'] = df['High'] - df['Low']
    df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
    df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    atr_values = df['TR'].rolling(window=window).mean()
    return df["Date"], atr_values

# 7. Stochastic Oscillator (STOCH)
def stochastic_oscillator(df, window=14):
    low_min = df["Low"].rolling(window=window).min()
    high_max = df["High"].rolling(window=window).max()
    stochastic = 100 * ((df["Close"] - low_min) / (high_max - low_min))
    return df["Date"], stochastic

# 8. Commodity Channel Index (CCI)
def cci(df, window=20):
    ma = df["Close"].rolling(window=window).mean()
    mad = (df["Close"] - ma).abs().rolling(window=window).mean()
    cci_values = (df["Close"] - ma) / (0.015 * mad)
    return df["Date"], cci_values

# 9. Parabolic SAR (SAR)
def parabolic_sar(df, step=0.02, max_step=0.2):
    psar = [df["Low"].iloc[0]]  # Starting with the first low
    up = True  # True if trend is up
    af = step  # Acceleration factor
    ep = df["High"].iloc[0]  # Extreme point (highest high)
    for i in range(1, len(df)):
        if up:
            psar.append(psar[-1] + af * (ep - psar[-1]))
            if df["Close"].iloc[i] < psar[-1]:
                up = False
                psar[-1] = ep
                ep = df["Low"].iloc[i]
                af = step
        else:
            psar.append(psar[-1] + af * (ep - psar[-1]))
            if df["Close"].iloc[i] > psar[-1]:
                up = True
                psar[-1] = ep
                ep = df["High"].iloc[i]
                af = step
        af = min(af + step, max_step)
    return df["Date"], pd.Series(psar, index=df.index)

# 10. On-Balance Volume (OBV)
def obv(df):
    obv_values = [0]
    for i in range(1, len(df)):
        if df["Close"].iloc[i] > df["Close"].iloc[i - 1]:
            obv_values.append(obv_values[-1] + df["Volume"].iloc[i])
        elif df["Close"].iloc[i] < df["Close"].iloc[i - 1]:
            obv_values.append(obv_values[-1] - df["Volume"].iloc[i])
        else:
            obv_values.append(obv_values[-1])
    return df["Date"], pd.Series(obv_values, index=df.index)
