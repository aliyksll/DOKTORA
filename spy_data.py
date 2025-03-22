import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_spy_data(start_date=None, end_date=None):
    """
    SPY (S&P 500 ETF) verilerini çeker.
    
    Args:
        start_date (str): Başlangıç tarihi (YYYY-MM-DD formatında)
        end_date (str): Bitiş tarihi (YYYY-MM-DD formatında)
        
    Returns:
        pandas.DataFrame: SPY verileri
    """
    # Tarihleri ayarla
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
        
    print(f"SPY verileri çekiliyor...")
    print(f"Tarih aralığı: {start_date} - {end_date}")
    
    try:
        # SPY ticker'ını oluştur
        spy = yf.Ticker("SPY")
        
        # Verileri çek
        df = spy.history(start=start_date, end=end_date)
        
        if df.empty:
            raise Exception("SPY için veri çekilemedi!")
            
        print("\nVeri başarıyla çekildi!")
        print(f"Toplam veri noktası: {len(df)}")
        print("\nİlk 5 veri noktası:")
        print(df.head())
        print("\nSon 5 veri noktası:")
        print(df.tail())
        
        # Verileri CSV dosyasına kaydet
        csv_filename = f"spy_data_{start_date}_{end_date}.csv"
        df.to_csv(csv_filename)
        print(f"\nVeriler {csv_filename} dosyasına kaydedildi.")
        
        return df
        
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
        return None

if __name__ == "__main__":
    # Son 1 yıllık veriyi çek
    spy_data = get_spy_data() 