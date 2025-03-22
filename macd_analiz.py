import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
from telegram import Bot
from dotenv import load_dotenv
import psycopg2
import warnings
import requests
import schedule

# Uyarıları görmezden gel
warnings.filterwarnings('ignore')

# .env dosyasından değişkenleri yükle
load_dotenv()

# Telegram bot bilgileri
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

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

def get_stock_data(symbol: str) -> pd.DataFrame:
    """
    Yahoo Finance'den günlük hisse verilerini çeker
    """
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}.IS"
    
    # Bugünün tarihini al
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)
    
    # Unix timestamp'e çevir
    period1 = int(start_date.timestamp())
    period2 = int(end_date.timestamp())
    
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
    """Günlük hisse verilerini veritabanına kaydeder"""
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
        print(f"{hisse_kodu} için günlük veriler kaydedildi.")
        
    except Exception as e:
        print(f"Veri kaydetme hatası ({hisse_kodu}): {e}")
        conn.rollback()
    finally:
        if cur:
            cur.close()

def macd_hesapla(df: pd.DataFrame, fast=12, slow=26, signal=9) -> pd.DataFrame:
    """
    MACD indikatörünü hesaplar
    """
    # EMA hesapla
    exp1 = df['Close'].ewm(span=fast, adjust=False).mean()
    exp2 = df['Close'].ewm(span=slow, adjust=False).mean()
    
    # MACD çizgisi
    df['MACD'] = exp1 - exp2
    
    # Sinyal çizgisi
    df['Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
    
    # Histogram
    df['Histogram'] = df['MACD'] - df['Signal']
    
    return df

def macd_sinyal_kaydet(conn, hisse_kodu: str, df: pd.DataFrame):
    """MACD sinyallerini veritabanına kaydeder"""
    try:
        cur = conn.cursor()
        
        # Son günün verilerini al
        son_gun = df.iloc[-1]
        tarih = son_gun.name.strftime('%Y-%m-%d')
        
        # Sinyal tipini belirle
        if son_gun['MACD'] > son_gun['Signal']:
            sinyal_tipi = 'AL'
        else:
            sinyal_tipi = 'SAT'
        
        # Veriyi ekle
        cur.execute("""
            INSERT INTO macd_sinyalleri 
            (hisse_kodu, tarih, sinyal_tipi, macd, sinyal, histogram)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (hisse_kodu, tarih) DO UPDATE SET
                sinyal_tipi = EXCLUDED.sinyal_tipi,
                macd = EXCLUDED.macd,
                sinyal = EXCLUDED.sinyal,
                histogram = EXCLUDED.histogram
        """, (
            hisse_kodu,
            tarih,
            sinyal_tipi,
            float(son_gun['MACD']),
            float(son_gun['Signal']),
            float(son_gun['Histogram'])
        ))
        
        conn.commit()
        return sinyal_tipi
        
    except Exception as e:
        print(f"MACD sinyal kaydetme hatası ({hisse_kodu}): {e}")
        conn.rollback()
        return None
    finally:
        if cur:
            cur.close()

async def sinyal_gonder(mesaj: str):
    """Telegram üzerinden sinyal gönderir"""
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=mesaj,
            parse_mode='HTML'  # HTML formatında mesaj gönder
        )
        print("Telegram mesajı başarıyla gönderildi.")
    except Exception as e:
        print(f"Sinyal gönderilirken hata oluştu: {e}")
    finally:
        try:
            if bot:
                await bot.close()
        except:
            pass

def hisse_analiz_et(hisse_kodu: str) -> str:
    """
    Bir hisse senedi için MACD analizi yapar
    """
    try:
        # Veritabanı bağlantısı
        conn = db_baglanti()
        if conn is None:
            return None
        
        # Günlük veriyi al
        df = get_stock_data(hisse_kodu)
        
        # Veriyi kaydet
        veri_kaydet(conn, hisse_kodu, df)
        
        # Son 50 günlük veriyi al
        cur = conn.cursor()
        cur.execute("""
            SELECT tarih, kapanis 
            FROM hisse_verileri 
            WHERE hisse_kodu = %s 
            ORDER BY tarih DESC 
            LIMIT 50
        """, (hisse_kodu,))
        
        veriler = cur.fetchall()
        if not veriler:
            return None
        
        # DataFrame oluştur
        df = pd.DataFrame(veriler, columns=['Date', 'Close'])
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        df.sort_index(inplace=True)
        
        # MACD hesapla
        df = macd_hesapla(df)
        
        # Sinyali kaydet ve döndür
        sinyal_tipi = macd_sinyal_kaydet(conn, hisse_kodu, df)
        
        if sinyal_tipi:
            son_fiyat = df['Close'].iloc[-1]
            return f"{hisse_kodu} {sinyal_tipi} - Fiyat: {son_fiyat:.2f} TL"
        
        return None
        
    except Exception as e:
        print(f"Hata: {hisse_kodu} analiz edilirken bir sorun oluştu - {e}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

async def tum_hisseleri_tara():
    """
    Tüm hisseleri tarar ve sinyalleri gönderir
    """
    print(f"Tarama başladı: {datetime.now()}")
    
    sinyaller = []
    for hisse in HISSELER:
        sinyal = hisse_analiz_et(hisse)
        if sinyal:
            sinyaller.append(sinyal)
    
    if sinyaller:
        mesaj = "🔔 <b>MACD Sinyalleri</b> 🔔\n\n" + "\n".join(sinyaller)
        mesaj += f"\n\n📅 <i>Tarama Zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M')}</i>"
        await sinyal_gonder(mesaj)
    else:
        print("Sinyal bulunamadı.")

async def main():
    """
    Ana program döngüsü
    """
    print("Bot başlatıldı!")
    print("Her gün saat 20:00'de tarama yapılacak...")
    
    # İlk taramayı hemen yap
    await tum_hisseleri_tara()
    
    # Her gün saat 20:00'de tarama yap
    schedule.every().day.at("20:00").do(
        lambda: asyncio.create_task(tum_hisseleri_tara())
    )
    
    while True:
        schedule.run_pending()
        await asyncio.sleep(60)  # Her dakika kontrol et

if __name__ == "__main__":
    print("Bot başlatılıyor...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot kullanıcı tarafından durduruldu.") 