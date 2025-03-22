-- Veritabanını oluştur
CREATE DATABASE merhaba_dunya_db;

-- Kullanıcı girişleri tablosu
CREATE TABLE IF NOT EXISTS kullanici_girisleri (
    id SERIAL PRIMARY KEY,
    isim VARCHAR(100) NOT NULL,
    giris_zamani TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Uygulama çıktıları tablosu
CREATE TABLE IF NOT EXISTS uygulama_ciktilari (
    id SERIAL PRIMARY KEY,
    mesaj TEXT NOT NULL,
    kullanici_id INTEGER REFERENCES kullanici_girisleri(id),
    tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Hisse verileri tablosu
CREATE TABLE IF NOT EXISTS hisse_verileri (
    id SERIAL PRIMARY KEY,
    hisse_kodu VARCHAR(10) NOT NULL,
    tarih DATE NOT NULL,
    acilis DECIMAL(10,2) NOT NULL,
    kapanis DECIMAL(10,2) NOT NULL,
    en_yuksek DECIMAL(10,2) NOT NULL,
    en_dusuk DECIMAL(10,2) NOT NULL,
    hacim BIGINT NOT NULL,
    UNIQUE(hisse_kodu, tarih)
);

-- MACD sinyalleri tablosu
CREATE TABLE IF NOT EXISTS macd_sinyalleri (
    id SERIAL PRIMARY KEY,
    hisse_kodu VARCHAR(10) NOT NULL,
    tarih DATE NOT NULL,
    sinyal_tipi VARCHAR(10) NOT NULL,  -- 'AL' veya 'SAT'
    macd DECIMAL(10,4) NOT NULL,
    sinyal DECIMAL(10,4) NOT NULL,
    histogram DECIMAL(10,4) NOT NULL,
    UNIQUE(hisse_kodu, tarih)
);

-- AlphaTrend sinyalleri tablosu
CREATE TABLE IF NOT EXISTS alpha_trend_sinyalleri (
    id SERIAL PRIMARY KEY,
    hisse_kodu VARCHAR(10) NOT NULL,
    sinyal_tipi VARCHAR(10) NOT NULL,  -- 'AL' veya 'SAT'
    fiyat DECIMAL(10,2) NOT NULL,
    tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 