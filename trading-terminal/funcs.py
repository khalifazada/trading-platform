#!/usr/bin/python

from requests import get
from time import time, sleep
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from scipy.stats import linregress

def data(symbol="BTCUSD", interval=15, limit=96, batch=1):
    frames = []
    for i in range(batch, 0, -1):
        time_url = "https://api-testnet.bybit.com/v2/public/time"
        server_time = get(time_url).json()["time_now"]
        ptime = int(float(server_time)) - i * limit * interval * 60
        data_url = f"https://api.bybit.com/v2/public/kline/list?symbol={symbol}&interval={interval}&limit={limit}&from={ptime}"
        res = get(data_url).json()['result']
        tmp_df = pd.DataFrame(res).iloc[:,3:7].astype('float')
        frames.append(tmp_df)
    df = pd.concat(frames, ignore_index=True)
    return df

def zsl(N=96, M=48, interval=15, batch=2):
    # get data
    d = data(interval=interval, limit=N, batch=batch)

    # calc hl2
    hl2 = (d.high + d.low) / 2

    # calc ema
    ema = hl2.ewm(span=M, adjust=False).mean()

    # calc std
    s = hl2.rolling(M).std()

    # calc z-score
    z = (hl2 - ema) / s

    # linreg z-score
    def get_slope(arr):
        y = np.array(arr)
        x = np.arange(len(y))
        m, b, _, _, _ = linregress(x,y)
        lreg = b + m * (M - 1)
        return lreg
    l = z.rolling(M).apply(get_slope)

    # calc stretched, centered logistic
    e = 2 * (((1 + np.exp(-l)) ** -1) - 0.5)

    return e[(batch * N // 2):], s[(batch * N // 2):], d[(batch * N // 2):], ema[(batch * N // 2):]
