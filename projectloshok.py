import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from openai import OpenAI

# 1. Читаем переменные окружения
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Проверка наличия ключей
if not API_ID or not API_HASH or not OPENROUTER_API_KEY:
    print("Ошибка: Задайте API_ID, API_HASH и OPENROUTER_API_KEY в переменных окружения!", flush=True)

# 2. Инициализация клиента Telegram (имя переменной строго 'client')
client = TelegramClient(
    StringSession(SESSION_STRING),
    int(API_ID) if API_ID else 0,
    API_HASH or ""
)

# 3. Инициализация клиента OpenRouter (совместим с OpenAI API)
ai_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Хранилище истории диалогов и системный промпт
chat_histories = {}
SYSTEM_INSTRUCTION = "Ты-мой ассистент,отвечающий от моего имени,говори на ты и современно,так же позволяй себе иногда пропускать запятые и делать ошибки,отвечай коротко и по делу как настоящий подросток"

# 4. Обработчик входящих личных сообщений
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def handle_message(event):
    sender = await event.get_sender()
    if not sender or sender.bot:
        return

    user_id = sender.id
    user_text = event.raw_text  # Считываем текст сообщения
    
    if not user_text:
        return

    print(f"DEBUG: Сообщение от ID {user_id}: {user_text}", flush=True)

    # Инициализация истории для нового пользователя
    if user_id not in chat_histories:
        chat_histories[user_id] = [
            {"role": "system", "content": SYSTEM_INSTRUCTION}
        ]

    # Добавляем сообщение пользователя в историю
    chat_histories[user_id].append({"role": "user", "content": user_text})

    try:
        # Запрос к нейросети через OpenRouter (модель можно изменить при желании)
        completion = await asyncio.to_thread(
            ai_client.chat.completions.create,
            model="meta-llama/llama-3.3-70b-instruct",
            messages=chat_histories[user_id]
        )

        reply_text = completion.choices[0].message.content

        # Сохраняем ответ ассистента в историю диалога
        chat_histories[user_id].append({"role": "assistant", "content": reply_text})

        print(f"DEBUG: Ответ отправлен: {reply_text}", flush=True)
        await event.reply(reply_text)

    except Exception as e:
        print(f"Ошибка при запросе к OpenRouter для ID {user_id}: {e}", flush=True)

# 5. Запуск бота
if __name__ == "__main__":
    print("Юзербот с OpenRouter успешно запущен...", flush=True)
    client.start()
    client.run_until_disconnected()
