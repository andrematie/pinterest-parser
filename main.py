import time
import requests
import os
import asyncio
from telethon import TelegramClient

# --- ВАШІ ДАНІ ---
api_id = 36857783
api_hash = '9e9b351839fe7924fec7a5787c0aaf1c'
make_webhook_url = 'https://hook.eu1.make.com/oqyga7xrva5zqn1lqim7escwxu4uv4cf'

if __name__ == '__main__':
    import asyncio
    with client:
        client.loop.run_until_complete(main()) 
        
# --- КАНАЛИ ТА НАЛАШТУВАННЯ ---
channels = ['KD_gerls', 'teen2']
DB_FILE = 'sent_posts.txt'  # Файл, де зберігатимуться ID постів

client = TelegramClient('parser_session', api_id, api_hash)

def is_posted(post_id):
    """Перевіряє, чи цей пост вже відправлявся раніше"""
    if not os.path.exists(DB_FILE):
        return False
    with open(DB_FILE, 'r') as f:
        return str(post_id) in f.read().splitlines()

def save_post(post_id):
    """Записує ID поста, щоб не постити його знову"""
    with open(DB_FILE, 'a') as f:
        f.write(f"{post_id}\n")

async def main():
    channel_index = 0
    print("Бот запущений. Очікування нових постів...")
    
    while True:
        target_channel = channels[channel_index]
        print(f"--- Перевірка каналу: @{target_channel} ---")
        
        found_new = False
        # Перевіряємо останні 20 повідомлень у каналі
        async for message in client.iter_messages(target_channel, limit=20):
            
            # Шукаємо повідомлення з медіа (фото або відео), яке ми ще не бачили
            if (message.photo or message.video) and not is_posted(message.id):
                print(f"Знайдено новий контент! ID: {message.id}")
                
                # Завантажуємо файл тимчасово на комп'ютер
                path = await message.download_media()
                

                # Відправляємо дані

