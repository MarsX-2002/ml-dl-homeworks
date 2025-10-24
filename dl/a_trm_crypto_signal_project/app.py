# app.py
import streamlit as st
from fetch_data import fetch_ohlcv
from signals_utbot_pro import ut_bot_pro as generate_signals

st.title("TinyTrader - Live signals")
df = fetch_ohlcv()
df = generate_signals(df)
st.line_chart(df['close'].tail(200))
st.write(df[['close','ema_fast','ema_slow','rsi','signal']].tail(10))
