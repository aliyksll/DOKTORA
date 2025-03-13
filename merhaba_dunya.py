import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# .env dosyasından veritabanı bağlantı bilgilerini yükle
load_dotenv()

# Veritabanı bağlantı bilgileri
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

def veritabani_baglantisi_kur():
    """Veritabanı bağlantısını oluşturur"""
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def kullanici_girisini_kaydet(isim):
    """Kullanıcı girişini veritabanına kaydeder"""
    with veritabani_baglantisi_kur() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO kullanici_girisleri (isim) VALUES (%s) RETURNING id",
                (isim,)
            )
            return cur.fetchone()[0]

def uygulama_ciktisini_kaydet(mesaj, kullanici_giris_id):
    """Uygulama çıktısını veritabanına kaydeder"""
    with veritabani_baglantisi_kur() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO uygulama_ciktilari (mesaj, kullanici_giris_id) VALUES (%s, %s)",
                (mesaj, kullanici_giris_id)
            )

def main():
    try:
        # Kullanıcıdan isim al
        isim = input("Lütfen adınızı girin: ")
        
        # Kullanıcı girişini kaydet
        giris_id = kullanici_girisini_kaydet(isim)
        
        # Selamlama mesajını oluştur
        mesaj = f"Merhaba {isim}, Hoş geldiniz!"
        
        # Mesajı ekrana yazdır
        print(mesaj)
        
        # Uygulama çıktısını kaydet
        uygulama_ciktisini_kaydet(mesaj, giris_id)
        
    except Exception as e:
        print(f"Bir hata oluştu: {e}")

if __name__ == "__main__":
    main() 