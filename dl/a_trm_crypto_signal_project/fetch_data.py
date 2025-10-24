# fetch_data.py
import ccxt
import pandas as pd

exchange = ccxt.binance({'enableRateLimit': True})
symbol = 'BTC/USDT'
timeframe = '5m'        # 1m or 5m for faster signals
limit = 1000

def fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit):
    data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(data, columns=['ts','open','high','low','close','vol'])
    df['ts'] = pd.to_datetime(df['ts'], unit='ms')
    df.set_index('ts', inplace=True)
    return df

if __name__ == '__main__':
    df = fetch_ohlcv()
    print(df.tail())
