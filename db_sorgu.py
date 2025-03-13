import os
import psycopg2
from dotenv import load_dotenv

# .env dosyasından değişkenleri yükle
load_dotenv()

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

def sorgu_calistir(sorgu: str):
    """Verilen SQL sorgusunu çalıştırır ve sonuçları döndürür"""
    conn = db_baglanti()
    if conn is None:
        return None
    
    try:
        cur = conn.cursor()
        cur.execute(sorgu)
        sonuclar = cur.fetchall()
        return sonuclar
    except Exception as e:
        print(f"Sorgu hatası: {e}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def tablo_listele():
    """Veritabanındaki tüm tabloları listeler"""
    sorgu = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    """
    return sorgu_calistir(sorgu)

def tablo_icerik_goster(tablo_adi: str):
    """Belirtilen tablonun içeriğini gösterir"""
    sorgu = f"SELECT * FROM {tablo_adi} LIMIT 10"
    return sorgu_calistir(sorgu)

if __name__ == "__main__":
    # Örnek kullanım
    print("Veritabanındaki tablolar:")
    tablolar = tablo_listele()
    if tablolar:
        for tablo in tablolar:
            print(f"\nTablo: {tablo[0]}")
            icerik = tablo_icerik_goster(tablo[0])
            if icerik:
                for satir in icerik:
                    print(satir) 