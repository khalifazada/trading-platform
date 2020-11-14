#!/usr/bin/python

from requests import get
from time import time, sleep
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def data(symbol="BTCUSD", interval=15, limit=96):
    time_url = "https://api-testnet.bybit.com/v2/public/time"
    server_time = get(time_url).json()["time_now"]
    ptime = int(float(server_time)) - limit * interval * 60
    data_url = f"https://api.bybit.com/v2/public/kline/list?symbol={symbol}&interval={interval}&limit={limit}&from={ptime}"
    res = get(data_url).json()['result']
    df = pd.DataFrame(res).iloc[:,3:7].astype('float')
    return df

def viz(df):
    x = list(range(len(df)))
    d = go.Candlestick(x=x, open=df.open, high=df.high, low=df.low, close=df.close)
    fig = go.Figure(data=d)
    fig.update(layout_xaxis_rangeslider_visible=False)
    fig.show()

def zsl(N=96, interval=15):
    # get 2x data
    d = data(limit=2*N, interval=interval)

    # calc hl2 for 1x data & reset index
    hl2 = (d.high[-N:] + d.low[-N:]) / 2
    hl2.reset_index(drop=True, inplace=True)

    # calc hl2 for 2x data, calc ema, select last 1/2x & reset index
    hl2_long = (d.high + d.low) / 2
    ema = hl2_long.ewm(span=N, adjust=False).mean()[-N:]
    ema.reset_index(drop=True, inplace=True)

    # calc hl2 std for 2x data, select last 1/2x data & reset index
    s = hl2_long.rolling(N).std()[-N:]
    s.reset_index(drop=True, inplace=True)

    # calc z-score
    z = (hl2 - ema) / s

    # linreg z-score

    # calc stretched, centered logistic
    e = 2 * (((1 + np.exp(-z)) ** -1) - 0.5)

    return e, z, s, d
