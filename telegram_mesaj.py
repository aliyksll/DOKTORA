import os
from dotenv import load_dotenv
from telegram import Bot
import asyncio
from telegram.error import RetryAfter

# .env dosyasından değişkenleri yükle
load_dotenv()

# Bot token ve chat ID'yi al
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

async def mesaj_gonder(mesaj: str):
    """Telegram üzerinden mesaj gönderir"""
    bot = None
    try:
        # Bot nesnesini oluştur
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # Mesajı gönder
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=mesaj
        )
        
        print("Mesaj başarıyla gönderildi!")
        
    except RetryAfter as e:
        print(f"Çok fazla mesaj gönderildi. {e.retry_after} saniye sonra tekrar deneyin.")
    except Exception as e:
        print(f"Mesaj gönderilirken bir hata oluştu: {e}")
    finally:
        if bot:
            try:
                await bot.close()
            except Exception:
                pass

async def main():
    while True:
        try:
            # Kullanıcıdan mesaj al
            mesaj = input("Göndermek istediğiniz mesajı yazın (Çıkmak için 'q' yazın): ")
            
            if mesaj.lower() == 'q':
                print("Program sonlandırılıyor...")
                break
            
            # Mesajı gönder
            await mesaj_gonder(mesaj)
            
        except Exception as e:
            print(f"Bir hata oluştu: {e}")

if __name__ == "__main__":
    try:
        # Asenkron fonksiyonu çalıştır
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram kullanıcı tarafından sonlandırıldı.") 