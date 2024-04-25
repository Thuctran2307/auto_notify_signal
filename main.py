import asyncio
import time
import numpy as np
import requests
import pandas as pd
import csv

from binance.client import Client
import pandas as pd
from telegram import Bot

api_key = 'PvxKOF52nJQvnRaSccmTKhsAY9Rgvd6mpbwMxep6tMatsoBTLrAJZPZ5BUxulfBH'
api_secret = 'cSGM6AXnpvXDX214P8AtVrZLOO3LHqBpNgrFM6TuXpklX8zF5MlfgF70SGVKZq4d'


def position_wvf(data):
    distance = 5
    for i in range(0,len(data['signal_wvf']),1):
        check = 0
        try:
            if data.loc[i, 'position_wvf'] == 1:
                for j in range(i - distance, i, 1):
                    if data.loc[j, 'position_wvf'] == 0:
                        check = 0
                    else:
                        check = check + 1
                if check == 0:
                    data.loc[i, 'position_wvf'] = -1
            else:
                if data.loc[i-1,'signal_wvf'] == 1 & data.loc[i,'signal_wvf'] == 0:
                    data.loc[i, 'position_wvf'] = 1
        except:
            pass
def save_candles_to_csv(candles, filename):
    if candles:
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume',
                          'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for candle in candles:
                writer.writerow({
                    'open_time': candle[0],
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5],
                    'close_time': candle[6],
                    'quote_asset_volume': candle[7],
                    'number_of_trades': candle[8],
                    'taker_buy_base_asset_volume': candle[9],
                    'taker_buy_quote_asset_volume': candle[10],
                    'ignore': candle[11]
                })
        print(f"Data saved to {filename}")
    else:
        print("No data to save.")

def get_recent_candles(symbol, limit=100):
    client = Client(api_key, api_secret)
    # start_time = '2023-01-01 00:00:00'
    # end_time = '2024-01-01 23:59:59'
    candles = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1HOUR, limit=limit)
    candles = pd.DataFrame(candles, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume',
                          'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    return candles

def get_data_from_csv(filename):
    data = pd.read_csv(filename)
    return data

def higest(index, prices_closed, loopback):
    return max(prices_closed[index-loopback:index])

def CM_Wiliam_Vix_Fix(data):
    
    pd_val = 22
    bbl_val = 20
    mult_val = 2.0
    lb_val = 50
    ph_val = 0.85
    pl_val = 1.01


    data['wvf'] = [0 for i in range(len(data))]
    data['upperBand'] = [0 for i in range(len(data))]
    data['rangeHigh'] = [0 for i in range(len(data))]
    data['sDev'] = [0 for i in range(len(data))]

    data['sDev'] = data['sDev'].astype(float)
    data['wvf'] = data['wvf'].astype(float)
    data['upperBand'] = data['upperBand'].astype(float)
    data['rangeHigh'] = data['rangeHigh'].astype(float)

    # Tính toán wvf
    
    for i in range(pd_val - 1,len(data),1):
        highest = np.max(data['close'].iloc[i - (pd_val - 1): i + 1])
        low = float(data.loc[i,'low'])
        data.loc[i,'wvf'] = (round(((float(highest) - float(low)) / float(highest)) * 100, 3))

    for i in range(bbl_val-1,len(data['wvf']),1):
        data.loc[i, 'sDev'] = float(round(mult_val * np.std(data['wvf'].iloc[i - (bbl_val - 1): i + 1]),3))
        
    midLine = pd.Series(data['wvf']).rolling(window=bbl_val).mean()

    # tính toán upperBand
    for i in range(1,len(data['sDev']) + 1):
        try:
            data.loc[i, 'upperBand'] = float(midLine[i] + data.loc[i,'sDev'])
        except:
            pass

    for i in range(lb_val,len(data['wvf']),1):
        highest = np.max(data['wvf'].iloc[i - lb_val: i])
        data.loc[i, 'upperBand'] = float(midLine[i] + data.loc[i,'sDev'])

def read_symbols_from_file(file_path):
    symbols = []
    with open(file_path, 'r') as file:
        for line in file:
            symbols.append(line.strip())
    return symbols

# lấy dữ liệu nến bằng request
def get_candles(symbol, interval, limit):
    url = f"https://binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    candles = response.json()
    # chuyển sang dạng dataframe
    candles = pd.DataFrame(candles, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume',
                          'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    return candles

list_symbol = ["BTCUSDT", "OPUSDT", "ETHUSDT", "WIFUSDT" ,'MANTAUSDT', 'BNBUSDT', 'RLCUSDT', 'RUNEUSDT', 'SOLUSDT']

# Thay thế 'YOUR_BOT_TOKEN' bằng mã token của bot Telegram của bạn
bot_token = '7090179855:AAHptMGZGRO72_I7Bn55hGz71lDbAHW1oPo'
# Thay thế 'YOUR_CHAT_ID' bằng chat ID của bạn
chat_id = '-4184438341'

async def alert(message):
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=message)

async def main():
    while True:
        
        for symbol in list_symbol:
            data = get_candles(symbol,'1h',100)
            CM_Wiliam_Vix_Fix(data)
            data['signal_wvf'] = np.where(data['wvf'] > data['upperBand'], 1.0, 0.0)
            data['signal_wvf'] = np.where(data['wvf'] > data['rangeHigh'], 1, data['signal_wvf'])

            
            data['position_wvf'] = [0 for i in range(len(data))]
            position_wvf(data)

            last_candle = data.loc[99,'position_wvf']
            print(f"Last candle: {last_candle}")
            
            if last_candle == 1:
                await alert(f"BUY {symbol}")
            elif last_candle == -1:
                await alert(f"SELL {symbol}")
            # nghỉ 2 phút
            print(f"{symbol} Không có tín hiệu!")
            time.sleep(30)
        time.sleep(3600)

asyncio.run(main())