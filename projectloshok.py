from telethon.sessions import StringSession
import os
import asyncio
from telethon import TelegramClient, events
from google import genai

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION_STRING = os.getenv("SESSION_STRING", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
gemini_client = genai.Client(api_key=GEMINI_API_KEY)


chats = {}

SYSTEM_INSTRUCTION = """
Ты — мой персональный ИИ-ассистент, который общается в личных сообщениях Telegram от моего имени.
Отвечай современно, естественным и нейтральным тоном.
Пиши кратко и емко, как человек в мессенджере (без длинных формальных эссе, если не просят).
Если просят что-то решить - реши как обычно решаешь
"""

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def handle_message(event):
    sender = await event.get_sender()
    if not sender or sender.bot:
        return

    user_id = sender.id
    user_text = event.raw_text

    print(f"DEBUG: Пришло сообщение от ID {user_id}: {user_text}", flush=True)

    try:
        # 1. Создаем чат с Gemini, если его еще нет
        if user_id not in chats:
            chats[user_id] = gemini_client.chats.create(
                model='gemini-2.0-flash',
                config={
                    'system_instruction': SYSTEM_INSTRUCTION  # Без опечаток
                }
            )

        # 2. ВСТАВЛЯЕМ СТРОЧКИ ДЛЯ ПОЛУЧЕНИЯ И ОТПРАВКИ ОТВЕТА ИИ:
        response = chats[user_id].send_message(user_text)
        print(f"DEBUG: Gemini ответил: {response.text}", flush=True)

        # 3. Отправляем ответ пользователю в Telegram
        await event.reply(response.text)

    except Exception as e:
        print(f"Ошибка при обработке сообщения от {user_id}: {e}", flush=True)


if __name__ == '__main__':
    print("Юзербот с Gemini успешно запущен...")
    try:
        with client:
            client.run_until_disconnected()
    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА В РАБОТЕ БОТА: {e}")
