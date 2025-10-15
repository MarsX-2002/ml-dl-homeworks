# bot.py
import time, logging
from telegram import Bot
from fetch_data import fetch_ohlcv
from signals import generate_signals

TELEGRAM_TOKEN = 'YOUR_TOKEN'
CHAT_ID = '@your_paid_channel_or_userid'
bot = Bot(TELEGRAM_TOKEN)

def publish_latest():
    df = fetch_ohlcv()
    df = generate_signals(df)
    last = df.iloc[-1]
    if last['signal'] == 1:
        text = f"LONG signal BTC/USDT @ {last['close']:.2f} (rsi {last['rsi']:.1f})"
    elif last['signal'] == -1:
        text = f"SHORT signal BTC/USDT @ {last['close']:.2f} (rsi {last['rsi']:.1f})"
    else:
        text = f"No signal. Price {last['close']:.2f}"
    bot.send_message(CHAT_ID, text)

if __name__ == '__main__':
    while True:
        try:
            publish_latest()
        except Exception as e:
            print("Err", e)
        time.sleep(60*5)  # match timeframe
