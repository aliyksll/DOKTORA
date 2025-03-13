# BIST AlphaTrend Bot

Bu proje, Borsa İstanbul'da işlem gören hisseler için AlphaTrend indikatörüne göre alım-satım sinyalleri üreten bir Telegram botudur.

## Özellikler

- BIST hisselerinin AlphaTrend indikatörünü hesaplar
- Telegram üzerinden alım-satım sinyalleri gönderir
- Piyasa saatleri içinde otomatik tarama yapar
- PostgreSQL veritabanı entegrasyonu

## Kurulum

1. Gerekli Python paketlerini yükleyin:
```bash
pip install -r requirements.txt
```

2. `.env` dosyası oluşturun ve aşağıdaki değişkenleri ekleyin:
```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=your_db_port
```

3. Veritabanı tablolarını oluşturun:
```bash
psql -d your_db_name -f schema.sql
```

## Kullanım

Bot'u başlatmak için:
```bash
nohup python bist_alpha_trend.py > bot.log 2>&1 &
```

Bot'u durdurmak için:
```bash
pkill -f bist_alpha_trend.py
```

## Veritabanı Sorguları

Veritabanı sorguları için `db_sorgu.py` scriptini kullanabilirsiniz:
```bash
python db_sorgu.py
```

## Lisans

MIT
