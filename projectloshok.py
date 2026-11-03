from telethon import TelegramClient, events
from telethon.sessions import StringSession
import os

# Инициализация клиента Telegram строго с именем client
client = TelegramClient(
    StringSession(os.getenv("SESSION_STRING")),
    int(os.getenv("API_ID")),
    os.getenv("API_HASH")
)

# Дальше идет ваш декоратор и обработчик
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def handle_message(event):
    ...
    sender = await event.get_sender()
    if not sender or sender.bot:
        return

    user_id = sender.id
    user_text = event.raw_text
    print(f"DEBUG: Сообщение от {user_id}: {user_text}", flush=True)

    # Инициализация истории, если пользователя еще нет в словаре
    if user_id not in chat_histories:
        chat_histories[user_id] = [
            {"role": "system", "content": SYSTEM_INSTRUCTION}
        ]

    # Добавляем входящее сообщение
    chat_histories[user_id].append({"role": "user", "content": user_text})

    try:
        # Вызов API OpenRouter (можно выбрать любую модель: meta-llama/llama-3.3-70b-instruct, openai/gpt-4o-mini, anthropic/claude-3.5-haiku и т.д.)
        completion = await asyncio.to_thread(
            ai_client.chat.completions.create,
            model="meta-llama/llama-3.3-70b-instruct",
            messages=chat_histories[user_id]
        )

        reply_text = completion.choices[0].message.content

        # Сохраняем ответ ИИ в историю
        chat_histories[user_id].append({"role": "assistant", "content": reply_text})

        print(f"DEBUG: Ответил: {reply_text}", flush=True)
        await event.reply(reply_text)

    except Exception as e:
        print(f"Ошибка OpenRouter для ID {user_id}: {e}", flush=True)


if __name__ == '__main__':
    print("Юзербот с Gemini успешно запущен...")
    try:
        with client:
            client.run_until_disconnected()
    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА В РАБОТЕ БОТА: {e}")
