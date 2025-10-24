import numpy as np
import pandas as pd
from signals_utbot_pro import ut_bot_pro
from fetch_data import fetch_ohlcv

def backtest_utbot(symbol='BTC/USDT', timeframe='5m', key_value=1.0, atr_period=10, confirm_bars=2, fee=0.001):
    """
    Backtest UT Bot Pro strategy
    Returns trade log + summary stats
    """
    df = fetch_ohlcv(symbol, timeframe)
    df = ut_bot_pro(df, key_value, atr_period, confirm_bars)

    capital = 1000.0
    position = 0.0
    entry_price = 0.0
    trades = []

    for i in range(len(df)):
        sig = df['signal'].iloc[i]
        price = df['close'].iloc[i]

        if sig == 1 and position <= 0:
            if position < 0:  # closing short
                capital += abs(position) * price
                position = 0
            size = (capital * 0.1) / price
            capital -= size * price
            entry_price = price
            position += size
            trades.append({'side': 'BUY', 'price': price, 'capital': capital, 'ts': df.index[i]})

        elif sig == -1 and position >= 0:
            if position > 0:  # closing long
                capital += position * price
                position = 0
            size = (capital * 0.1) / price
            capital += size * price
            entry_price = price
            position -= size
            trades.append({'side': 'SELL', 'price': price, 'capital': capital, 'ts': df.index[i]})

        # apply small fee each trade
        if sig != 0:
            capital -= capital * fee

    # close any open pos at last price
    if position != 0:
        capital += position * df['close'].iloc[-1]
        position = 0

    # Build trade log
    trades_df = pd.DataFrame(trades)
    if len(trades_df) == 0:
        print("No trades found.")
        return None, None

    trades_df['return'] = trades_df['capital'].pct_change() * 100
    total_return = (capital / 1000.0 - 1) * 100
    win_trades = trades_df[trades_df['return'] > 0]
    win_rate = len(win_trades) / len(trades_df) * 100

    summary = {
        'Symbol': symbol,
        'Timeframe': timeframe,
        'Trades': len(trades_df),
        'WinRate (%)': round(win_rate, 2),
        'Final Capital ($)': round(capital, 2),
        'Total Return (%)': round(total_return, 2)
    }

    return trades_df, summary


if __name__ == '__main__':
    trades_df, summary = backtest_utbot(
    symbol='BTC/USDT',
    timeframe='5m',
    key_value=0.25,     # lower = more signals
    atr_period=3,       # more responsive ATR
    confirm_bars=1,     # immediate confirmation
    fee=0.0005
)

if trades_df is not None:
    print(pd.DataFrame([summary]))
    print(trades_df.tail(10))


