# signals.py
import pandas as pd, numpy as np
import pandas_ta as ta
from fetch_data import fetch_ohlcv

def generate_signals(df):
    df = df.copy()
    df['ema_fast'] = ta.ema(df['close'], length=12)
    df['ema_slow'] = ta.ema(df['close'], length=26)
    df['rsi'] = ta.rsi(df['close'], length=14)
    df['signal'] = 0
    # basic long signal: fast ema crosses above slow & rsi < 70
    cond_long = (df['ema_fast'] > df['ema_slow']) & (df['ema_fast'].shift(1) <= df['ema_slow'].shift(1)) & (df['rsi'] < 70)
    cond_short = (df['ema_fast'] < df['ema_slow']) & (df['ema_fast'].shift(1) >= df['ema_slow'].shift(1)) & (df['rsi'] > 30)
    df.loc[cond_long, 'signal'] = 1
    df.loc[cond_short, 'signal'] = -1
    return df

if __name__ == '__main__':
    df = fetch_ohlcv()
    df = generate_signals(df)
    print(df[['close','ema_fast','ema_slow','rsi','signal']].tail(10))
