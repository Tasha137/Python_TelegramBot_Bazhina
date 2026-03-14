import telebot
from secrets import API_TOKEN

print(f"🔑 TOKEN: {API_TOKEN[:20]}...")
bot = telebot.TeleBot(API_TOKEN)
print("✅ Бот создан!")

user_states = {}
user_data = {}


@bot.message_handler(func=lambda m: True)  # ЛОВИТ ВСЕ СООБЩЕНИЯ!
def all_messages(message):
    user_id = message.from_user.id
    text = message.text.lower().strip()

    print(f"📨 '{message.text}' от {user_id}")

    # Команды по тексту
    if text == '/start':
        bot.reply_to(message, "🚀 Бот готов!\n\n"
                              "📝 Напиши 'создать' для создания события\n"
                              "📅 Напиши 'события' для просмотра\n"
                              "❌ Напиши 'отмена' для сброса")

    elif text == 'создать':
        user_states[user_id] = "waiting_name"
        user_data[user_id] = {}
        bot.reply_to(message, "📝 **НАЗВАНИЕ события:**\n(Маникюр, Стоматолог)")

    elif text == 'события':
        bot.reply_to(message, "📅 **ТВОИ СОБЫТИЯ:**\n• Маникюр | 23.03 | 11:00")

    elif text == 'отмена':
        if user_id in user_states:
            del user_states[user_id]
            del user_data[user_id]
        bot.reply_to(message, "❌ Отменено!")

    # Машина состояний
    elif user_id in user_states:
        state = user_states[user_id]

        if state == "waiting_name":
            user_data[user_id]["name"] = message.text
            user_states[user_id] = "waiting_date"
            bot.reply_to(message, "📅 **ДАТА** (2026-03-23):")

        elif state == "waiting_date":
            user_data[user_id]["date"] = message.text
            user_states[user_id] = "waiting_time"
            bot.reply_to(message, "🕐 **ВРЕМЯ** (11:00):")

        elif state == "waiting_time":
            user_data[user_id]["time"] = message.text
            name = user_data[user_id]["name"]
            date = user_data[user_id]["date"]
            time = user_data[user_id]["time"]
            bot.reply_to(message, f"✅ **СОЗДАНО!**\n{name} | {date} | {time}")
            # Очищаем состояние
            del user_states[user_id]
            del user_data[user_id]

    else:
        bot.reply_to(message, "❓ Напиши:\n• 'создать' — новое событие\n• 'события' — список\n• 'отмена' — сброс")


print("🎯 Запуск...")
bot.infinity_polling()
