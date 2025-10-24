# backtest.py
import numpy as np
from signals import generate_signals, fetch_ohlcv

def backtest(symbol='BTC/USDT', timeframe='5m'):
    df = fetch_ohlcv(symbol, timeframe)
    df = generate_signals(df)
    initial = 1000.0
    cash = initial
    pos = 0.0
    pnl_list = []
    for i in range(1,len(df)):
        sig = df['signal'].iloc[i]
        price = df['close'].iloc[i]
        if sig == 1 and pos == 0:
            # buy with 10% capital
            size = (cash * 0.1) / price
            cash -= size * price
            pos += size
        elif sig == -1 and pos > 0:
            cash += pos * price
            pos = 0
        net = cash + pos * price
        pnl_list.append(net)
    return pnl_list, initial

if __name__ == '__main__':
    pnl, initial = backtest()
    print('Return %:', (pnl[-1]/initial - 1)*100)
