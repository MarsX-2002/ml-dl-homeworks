import pandas as pd
import numpy as np
import pandas_ta as ta
from fetch_data import fetch_ohlcv

def ut_bot_pro(df, key_value=1.0, atr_period=10, confirm_bars=2):
    """
    UT Bot Pro - Heikin Ashi + ATR + Reversal Confirmation
    key_value: sensitivity (higher = fewer signals)
    atr_period: ATR window
    confirm_bars: bars to wait before confirming reversal
    """

    # ✅ Compute Heikin Ashi candles efficiently
    ha = ta.ha(open_=df['open'], high=df['high'], low=df['low'], close=df['close'])
    ha.columns = ['HA_open', 'HA_high', 'HA_low', 'HA_close']
    df = pd.concat([df, ha], axis=1)

    # ✅ Compute ATR for volatility
    df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=atr_period)

    # Initialize trailing stop + signal
    df['trend'] = 0   # 1 = long, -1 = short
    df['signal'] = 0  # 1 = buy, -1 = sell
    df['trail'] = np.nan

    long_trail = np.nan
    short_trail = np.nan
    trend = 0
    confirm_counter = 0

    for i in range(1, len(df)):
        close = df['HA_close'].iloc[i]
        atr = df['atr'].iloc[i]
        prev_close = df['HA_close'].iloc[i - 1]

        # Dynamic trailing levels
        if trend == 1:
            long_trail = max(long_trail, close - key_value * atr)
        elif trend == -1:
            short_trail = min(short_trail, close + key_value * atr)

        # Potential reversals
        if close > (short_trail if not np.isnan(short_trail) else -np.inf):
            confirm_counter += 1
            if confirm_counter >= confirm_bars:
                trend = 1
                long_trail = close - key_value * atr
                short_trail = np.nan
                df.loc[df.index[i], 'signal'] = 1
                confirm_counter = 0
        elif close < (long_trail if not np.isnan(long_trail) else np.inf):
            confirm_counter += 1
            if confirm_counter >= confirm_bars:
                trend = -1
                short_trail = close + key_value * atr
                long_trail = np.nan
                df.loc[df.index[i], 'signal'] = -1
                confirm_counter = 0
        else:
            confirm_counter = 0

        df.loc[df.index[i], 'trend'] = trend
        df.loc[df.index[i], 'trail'] = long_trail if trend == 1 else short_trail

    return df

if __name__ == '__main__':
    df = fetch_ohlcv()
    df = ut_bot_pro(df, key_value=1.0, atr_period=10, confirm_bars=2)
    print(df[['HA_close', 'trend', 'signal', 'trail']].tail(20))
