import telebot
import psycopg2
import ssl
import urllib3
from db_calendar import Calendar
from secrets import API_TOKEN
import os

os.environ["PYTHONWARNINGS"] = "ignore::urllib3.exceptions.InsecureRequestWarning"


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
telebot.apihelper.REQUEST_TIMEOUT = 30
telebot.apihelper.LONG_POLLING_TIMEOUT = 20

conn = psycopg2.connect(
    host="localhost",
    database="calendar_db",
    user="calendar_user",
    password="calendar_pass",
    port=5432,
)
calendar = Calendar(conn)
bot = telebot.TeleBot(API_TOKEN)

conn = psycopg2.connect(
    host="localhost",
    database="calendar_db",
    user="calendar_user",
    password="calendar_pass",
    port=5432,
)

calendar = Calendar(conn)

bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        """🗓️ Календарь-Помощник (PostgreSQL)
         
         📅 Календарь:
         /create_event <название> <дата> <время> <описание>
         /list_events
         /read_event <название>
         /edit_event <название> <новая_дата> <новое_описание>
         /delete_event <название>
         
         /Пример: /create_event Встреча 2026-03-15 14:00 тест""",
    )


@bot.message_handler(commands=["create_event"])
def create_event_handler(message):
    try:
        args = message.text.split()[1:]
        if len(args) < 4:
            bot.reply_to(
                message, "❌ /create_event <название> <дата> <время> <описание>"
            )
            return

        event_name, event_date, event_time = args[0], args[1], args[2]
        event_details = " ".join(args[3:])

        # ← ИСПОЛЬЗУЕТ ТВОЙ НОВЫЙ КЛАСС!
        if calendar.create_event(event_name, event_date, event_time, event_details):
            bot.reply_to(message, f"✅ Событие '{event_name}' создано в PostgreSQL!")
        else:
            bot.reply_to(message, "❌ Ошибка создания")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")


@bot.message_handler(commands=["list_events"])
def list_events_handler(message):
    try:
        # ← ИСПОЛЬЗУЕТ ТВОЙ НОВЫЙ КЛАСС!
        events = calendar.display_events()
        bot.reply_to(message, "📅 События сохранены в PostgreSQL!\n(Проверь консоль)")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")


@bot.message_handler(commands=["read_event"])
def read_event_handler(message):
    try:
        args = message.text.split()[1:]
        if not args:
            bot.reply_to(message, "❌ /read_event <название>")
            return

        event_name = args[0]
        # ← ИСПОЛЬЗУЕТ ТВОЙ НОВЫЙ КЛАСС!
        events = calendar.read_event(event_name)
        if events:
            bot.reply_to(
                message, f"✅ Найдено событие '{event_name}' (проверь консоль)"
            )
        else:
            bot.reply_to(message, "❌ Событие не найдено")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")


@bot.message_handler(commands=["edit_event"])
def edit_event_handler(message):
    try:
        args = message.text.split()[1:]
        if len(args) < 3:
            bot.reply_to(
                message, "❌ /edit_event <название> <новая_дата> <новое_описание>"
            )
            return

        event_name = args[0]
        new_date = args[1]
        new_details = " ".join(args[2:])

        # ← ИСПОЛЬЗУЕТ ТВОЙ НОВЫЙ КЛАСС!
        if calendar.edit_event(event_name, new_date, new_description=new_details):
            bot.reply_to(message, f"✅ Событие '{event_name}' обновлено!")
        else:
            bot.reply_to(message, "❌ Событие не найдено")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")


@bot.message_handler(commands=["delete_event"])
def delete_event_handler(message):
    try:
        args = message.text.split()[1:]
        if not args:
            bot.reply_to(message, "❌ /delete_event <название>")
            return

        event_name = args[0]
        # ← ИСПОЛЬЗУЕТ ТВОЙ НОВЫЙ КЛАСС!
        if calendar.delete_event(event_name):
            bot.reply_to(message, f"✅ Событие '{event_name}' удалено из PostgreSQL!")
        else:
            bot.reply_to(message, "❌ Событие не найдено")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")


print("🚀 Бот с PostgreSQL запущен!")
bot.infinity_polling()
