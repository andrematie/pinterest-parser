import os
import json
import asyncio
import requests
from telethon import TelegramClient

# --- НАЛАШТУВАННЯ ---
api_id = 36857783
api_hash = "9e9b351839fe7924fec7a5787c0aaf1c"
webhook_url = "https://hook.eu1.make.com/oqyga7xrva5zqn1lqim7escwxu4uv4cf"
session_name = "parser_session"

# Список каналів для парсингу
# last_id: 0 означає "почати з найпершого поста в історії". 
# Якщо треба почати з новіших, впиши сюди ID поста, з якого почати.
sources = [
    {"name": "KD_gerls", "last_id": 0},
    {"name": "teen2",    "last_id": 0}
]

# Файл для збереження прогресу (щоб не починати з нуля після перезапуску)
STATE_FILE = "parser_state.json"

client = TelegramClient(session_name, api_id, api_hash)

def load_state():
    """Завантажує ID останніх оброблених постів"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    # Якщо файлу немає, беремо налаштування за замовчуванням
    return {src["name"]: src["last_id"] for src in sources}

def save_state(state):
    """Зберігає прогрес у файл"""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

async def main():
    print("Бот запущений. Починаю читати історію...")
    state = load_state()
    
    # Індекс поточного каналу (0 - перший, 1 - другий)
    current_idx = 0

    while True:
        # Визначаємо, з якого каналу зараз беремо
        source = sources[current_idx]
        channel_name = source["name"]
        # Беремо ID, на якому зупинилися минулого разу
        last_id = state.get(channel_name, source["last_id"])
        
        print(f"--- Перевірка каналу: {channel_name} (шукаю після ID {last_id}) ---")

        try:
            # Шукаємо 1 повідомлення, яке НОВІШЕ за last_id (рухаємось від старого до нового)
            messages = await client.get_messages(
                channel_name, 
                limit=1, 
                min_id=last_id, 
                reverse=True # Це важливо: йдемо в хронологічному порядку
            )

            if not messages:
                print(f"У каналі {channel_name} закінчилися пости або немає нових.")
                # Чекаємо хвилину і переходимо до іншого каналу
                await asyncio.sleep(60)
                current_idx = (current_idx + 1) % len(sources)
                continue

            message = messages[0]
            new_id = message.id

            # Якщо є фото або відео
            if message.photo or message.video:
                print(f"Знайдено медіа (ID {new_id})! Завантажую...")
                file_path = await message.download_media()
                
                # Відправка на Make
                try:
                    with open(file_path, "rb") as f:
                        requests.post(
                            webhook_url, 
                            files={"file": f}, 
                            data={"caption": message.text or ""}
                        )
                    print(f"Успішно відправлено! Наступна публікація через 40 хв.")
                    
                    # Оновлюємо статус тільки після успішної відправки
                    state[channel_name] = new_id
                    save_state(state)
                    
                    # Видаляємо файл з диску
                    os.remove(file_path)
                    
                    # Передаємо чергу наступному каналу
                    current_idx = (current_idx + 1) % len(sources)
                    
                    # Чекаємо 40 хвилин (2400 секунд)
                    await asyncio.sleep(2400) 
                    
                except Exception as e:
                    print(f"Помилка відправки на Make: {e}")
                    await asyncio.sleep(60) # Спробуємо ще раз через хвилину
            else:
                # Якщо це просто текст — просто позначаємо як прочитане і йдемо далі відразу
                print(f"Пост ID {new_id} без медіа. Пропускаю...")
                state[channel_name] = new_id
                save_state(state)
                # Не чекаємо 40 хв, йдемо на наступне коло циклу відразу

        except Exception as e:
            print(f"Помилка при читанні каналу {channel_name}: {e}")
            await asyncio.sleep(60)

# Цей блок гарантує правильний запуск
if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
