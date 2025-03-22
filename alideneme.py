import pandas as pd
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
import datetime as dt
import yfinance as yf

def get_data():
    """
    Verilen bir hisse senedi için, belirtilen tarih aralığında getirileri hesaplar.

    """
    tickers = ['SPY', 'GLD', 'BTC-USD']
    end_date = dt.datetime.now()
    start_date = end_date - dt.timedelta(days=365*3)
    adj_close_df = pd.DataFrame()

    for ticker in tickers:  
        data = yf.download(ticker, start=start_date, end=end_date)
        data['Close'].plot(figsize=(10, 5))
        plt.title(f'{ticker} Fiyatları')
        plt.xlabel('Tarih')
        plt.ylabel('Fiyat')
        plt.show()
        adj_close_df[ticker] = data['Close']
        adj_close_df.dropna(inplace=True)
        adj_close_df.sort_index(inplace=True)
        adj_close_df.to_csv('adj_close_df.csv')
        print(f'{ticker} verileri kaydedildi.')
        print(adj_close_df)
        
    return adj_close_df

def main():
    """
    Ana fonksiyon.
    """
    get_data()

if __name__ == '__main__':
    main()