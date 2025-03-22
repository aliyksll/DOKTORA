import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv

# .env dosyasından değişkenleri yükle
load_dotenv()

# Telegram bot bilgileri
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def get_chat_id():
    """Bot'un bulunduğu tüm sohbetlerin ID'lerini listeler"""
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # Bot'un bilgilerini al
        bot_info = await bot.get_me()
        print(f"\nBot Bilgileri:")
        print(f"Bot ID: {bot_info.id}")
        print(f"Bot Kullanıcı Adı: @{bot_info.username}")
        print(f"Bot Adı: {bot_info.first_name}")
        
        # Son mesajları al
        updates = await bot.get_updates()
        if updates:
            print("\nBulunan Sohbetler:")
            for update in updates:
                if update.message:
                    chat = update.message.chat
                    print(f"\nSohbet ID: {chat.id}")
                    print(f"Sohbet Tipi: {chat.type}")
                    if chat.type == 'group':
                        print(f"Grup Adı: {chat.title}")
                    elif chat.type == 'private':
                        print(f"Kullanıcı Adı: {chat.username}")
        else:
            print("\nHenüz hiç mesaj alınmamış. Lütfen bota bir mesaj gönderin.")
            
    except Exception as e:
        print(f"Hata oluştu: {e}")
    finally:
        if bot:
            await bot.close()

if __name__ == "__main__":
    print("Telegram Chat ID Bulma Aracı")
    print("----------------------------")
    print("1. Botu gruba ekleyin")
    print("2. Grupta herhangi bir mesaj gönderin")
    print("3. Bu scripti çalıştırın")
    print("\nDevam etmek için Enter'a basın...")
    input()
    
    asyncio.run(get_chat_id()) 