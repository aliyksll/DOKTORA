import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import psycopg2
from dotenv import load_dotenv
import warnings
import requests
import schedule 
# Uyarıları görmezden gel
warnings.filterwarnings('ignore')

# .env dosyasından değişkenleri yükle
load_dotenv()

# BIST hisseleri
HISSELER = ['THYAO', 'TCELL']

def db_baglanti():
    """Veritabanı bağlantısı oluşturur"""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        return conn
    except Exception as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        return None

def get_stock_data(symbol: str, period1: int, period2: int) -> pd.DataFrame:
    """
    Yahoo Finance'den hisse verilerini çeker
    """
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}.IS"
    
    params = {
        "period1": period1,
        "period2": period2,
        "interval": "1d",
        "events": "history"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    if "chart" not in data or "result" not in data["chart"] or not data["chart"]["result"]:
        raise ValueError(f"Veri alınamadı: {symbol}")
        
    result = data["chart"]["result"][0]
    quotes = result["indicators"]["quote"][0]
    
    df = pd.DataFrame({
        "Open": quotes["open"],
        "High": quotes["high"],
        "Low": quotes["low"],
        "Close": quotes["close"],
        "Volume": quotes["volume"]
    }, index=pd.to_datetime(result["timestamp"], unit="s"))
    
    return df

def veri_kaydet(conn, hisse_kodu: str, df: pd.DataFrame):
    """Hisse verilerini veritabanına kaydeder"""
    try:
        cur = conn.cursor()
        
        for tarih, row in df.iterrows():
            # NaN değerleri kontrol et
            if pd.isna(row['Open']) or pd.isna(row['Close']) or pd.isna(row['High']) or pd.isna(row['Low']) or pd.isna(row['Volume']):
                print(f"UYARI: {hisse_kodu} için {tarih} tarihinde eksik veri var, bu kayıt atlanıyor.")
                continue
                
            # Tarih formatını düzenle
            tarih_str = tarih.strftime('%Y-%m-%d')
            
            # Veriyi ekle
            cur.execute("""
                INSERT INTO hisse_verileri 
                (hisse_kodu, tarih, acilis, kapanis, en_yuksek, en_dusuk, hacim)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (hisse_kodu, tarih) DO UPDATE SET
                    acilis = EXCLUDED.acilis,
                    kapanis = EXCLUDED.kapanis,
                    en_yuksek = EXCLUDED.en_yuksek,
                    en_dusuk = EXCLUDED.en_dusuk,
                    hacim = EXCLUDED.hacim
            """, (
                hisse_kodu,
                tarih_str,
                float(row['Open']),
                float(row['Close']),
                float(row['High']),
                float(row['Low']),
                int(row['Volume'])
            ))
        
        conn.commit()
        print(f"{hisse_kodu} için veriler kaydedildi.")
        
    except Exception as e:
        print(f"Veri kaydetme hatası ({hisse_kodu}): {e}")
        conn.rollback()
    finally:
        if cur:
            cur.close()

def main():
    """
    Ana program
    """
    print("Geçmiş veri toplama işlemi başlatıldı...")
    
    # Veritabanı bağlantısı
    conn = db_baglanti()
    if conn is None:
        return
    
    try:
        # Bugünün tarihini al
        end_date = datetime.now()
        # 1 yıl öncesini al
        start_date = end_date - timedelta(days=365)
        
        # Unix timestamp'e çevir
        period1 = int(start_date.timestamp())
        period2 = int(end_date.timestamp())
        
        # Her hisse için veri topla
        for hisse in HISSELER:
            print(f"\n{hisse} için veri toplanıyor...")
            try:
                # Veriyi al
                df = get_stock_data(hisse, period1, period2)
                
                # Veriyi kaydet
                veri_kaydet(conn, hisse, df)
                
            except Exception as e:
                print(f"Hata: {hisse} için veri toplanırken bir sorun oluştu - {e}")
                continue
        
        print("\nGeçmiş veri toplama işlemi tamamlandı!")
        
    except Exception as e:
        print(f"Genel hata: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main() 