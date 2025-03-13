import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
from telegram import Bot
from dotenv import load_dotenv
import schedule
import time
import requests
import json
import warnings

# Uyarıları görmezden gel
warnings.filterwarnings('ignore')

# .env dosyasından değişkenleri yükle
load_dotenv()

# Telegram bot bilgileri
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# BIST hisseleri
HISSELER = [
    'THYAO.IS', 'GARAN.IS', 'ASELS.IS', 'SASA.IS', 'KRDMD.IS',
    'EREGL.IS', 'BIMAS.IS', 'AKBNK.IS', 'YKBNK.IS', 'PGSUS.IS'
]

def get_stock_data(symbol: str, period1: int, period2: int) -> pd.DataFrame:
    """
    Yahoo Finance'den hisse verilerini çeker
    """
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    
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

def alpha_trend(data: pd.DataFrame, period: int = 14, multiplier: float = 2.0) -> pd.DataFrame:
    """
    AlphaTrend indikatörünü hesaplar
    """
    high = data['High']
    low = data['Low']
    close = data['Close']
    
    # TR (True Range) hesaplama
    tr = pd.DataFrame()
    tr['h-l'] = high - low
    tr['h-pc'] = abs(high - close.shift(1))
    tr['l-pc'] = abs(low - close.shift(1))
    tr['tr'] = tr[['h-l', 'h-pc', 'l-pc']].max(axis=1)
    
    # ATR hesaplama
    atr = tr['tr'].rolling(period).mean()
    
    # AlphaTrend hesaplama
    up = low - (multiplier * atr)
    up1 = up.copy()
    
    for i in range(period, len(up)):
        if close[i-1] > up1[i-1] and close[i] > up[i]:
            up[i] = max(up[i], up1[i-1])
        elif close[i] > up[i]:
            up[i] = up[i]
        else:
            up[i] = up[i]
    
    down = high + (multiplier * atr)
    down1 = down.copy()
    
    for i in range(period, len(down)):
        if close[i-1] < down1[i-1] and close[i] < down[i]:
            down[i] = min(down[i], down1[i-1])
        elif close[i] < down[i]:
            down[i] = down[i]
        else:
            down[i] = down[i]
    
    # Trend belirleme
    data['AlphaTrend'] = np.nan
    data.loc[close > down, 'AlphaTrend'] = 1  # Yukarı trend
    data.loc[close < up, 'AlphaTrend'] = -1   # Aşağı trend
    
    return data

async def sinyal_gonder(mesaj: str):
    """Telegram üzerinden sinyal gönderir"""
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=mesaj,
            parse_mode='HTML'  # HTML formatında mesaj gönder
        )
    except Exception as e:
        print(f"Sinyal gönderilirken hata oluştu: {e}")
    finally:
        if bot:
            await bot.close()

def hisse_analiz_et(hisse_kodu: str) -> str:
    """
    Bir hisse senedi için AlphaTrend analizi yapar
    """
    try:
        # Tarih aralığını belirle
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)  # Son 30 günlük veri
        
        # Unix timestamp'e çevir
        period1 = int(start_date.timestamp())
        period2 = int(end_date.timestamp())
        
        # Veriyi al
        hisse_data = get_stock_data(hisse_kodu, period1, period2)
        
        if hisse_data.empty:
            return None
        
        # AlphaTrend hesapla
        hisse_data = alpha_trend(hisse_data)
        
        # Son iki günün verilerini al
        son_iki_gun = hisse_data.tail(2)
        
        if len(son_iki_gun) < 2:
            return None
            
        onceki_trend = son_iki_gun.iloc[0]['AlphaTrend']
        guncel_trend = son_iki_gun.iloc[1]['AlphaTrend']
        guncel_fiyat = son_iki_gun.iloc[1]['Close']
        
        # Sinyal kontrolü
        temiz_kod = hisse_kodu.replace('.IS', '')
        if onceki_trend == -1 and guncel_trend == 1:
            return f"🟢 <b>AL Sinyali:</b> {temiz_kod} - Fiyat: {guncel_fiyat:.2f} TL"
        elif onceki_trend == 1 and guncel_trend == -1:
            return f"🔴 <b>SAT Sinyali:</b> {temiz_kod} - Fiyat: {guncel_fiyat:.2f} TL"
            
        return None
        
    except Exception as e:
        print(f"Hata: {hisse_kodu} analiz edilirken bir sorun oluştu - {e}")
        return None

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
        mesaj = "🔔 <b>AlphaTrend Sinyalleri</b> 🔔\n\n" + "\n".join(sinyaller)
        mesaj += f"\n\n📅 <i>Tarama Zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M')}</i>"
        await sinyal_gonder(mesaj)
    else:
        print("Sinyal bulunamadı.")

async def main():
    """
    Ana program döngüsü
    """
    print("Bot başlatıldı!")
    print("Piyasa saatleri içinde her saat başı tarama yapılacak...")
    
    # İlk taramayı hemen yap
    await tum_hisseleri_tara()
    
    # Piyasa saatleri içinde her saat başı tarama yap (10:00-18:00)
    for saat in range(10, 19):
        schedule.every().day.at(f"{saat:02d}:00").do(
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