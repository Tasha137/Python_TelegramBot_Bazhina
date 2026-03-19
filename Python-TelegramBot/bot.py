import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calendar_admin.settings")
django.setup()

import telebot
import psycopg2
import ssl
import urllib3
from db_calendar import Calendar
from secrets_bot import API_TOKEN
from events.utils import get_today_stats

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

    stat = get_today_stats()
    stat.user_count += 1
    stat.save()


@bot.message_handler(commands=["create_event"])
def create_event_handler(message):
    try:
        args = message.text.split()[1:]
        if len(args) < 4:
            bot.reply_to(message, "❌ /create_event <название> <дата> <время> <описание>")
            return

        event_name, event_date, event_time = args[0], args[1], args[2]

        if calendar.create_event(event_name, event_date, event_time):  # убрали event_details
            bot.reply_to(message, f"✅ Событие '{event_name}' создано в PostgreSQL!")
        else:
            bot.reply_to(message, "❌ Ошибка создания")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

    stat = get_today_stats()
    stat.event_count += 1
    stat.save()

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

    stat = get_today_stats()
    stat.event_count += 1
    stat.save()

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

    stat = get_today_stats()
    stat.event_count += 1
    stat.save()


@bot.message_handler(commands=["invite"])
def invite_handler(message):
    try:
        args = message.text.split()[1:]
        if len(args) < 2:
            bot.reply_to(message, "❌ /invite @username <название_события>")
            return

        username = args[0].lstrip("@")
        event_name = " ".join(args[1:])

        inviter_id = message.from_user.id

        from events.models import Event
        try:
            event = Event.objects.filter(name__icontains=event_name).first()
            if not event:
                bot.reply_to(message, f"❌ Событие '{event_name}' не найдено")
                return
        except Exception:
            bot.reply_to(message, f"❌ Событие '{event_name}' не найдено")
            return

        from events.utils import is_user_free
        is_free, free_msg = True, "Свободен"

        if not is_free:
            bot.reply_to(message, f"❌ {free_msg}")
            return

        from events.models import EventParticipant
        participant, created = EventParticipant.objects.get_or_create(
            event=event,
            user_id=1,
            defaults={"status": "pending"},
        )

        if created:
            status_text = "✅ Приглашение отправлено (ожидание)"
        else:
            status_text = "ℹ️ Приглашение уже существует (обновлено на ожидание)"

        bot.reply_to(message, f"{status_text}\n📅 {event.date} {event.time}")

        stat = get_today_stats()
        stat.event_count += 1
        stat.save()

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка приглашения: {str(e)}")


@bot.message_handler(func=lambda m: m.text.startswith("/accept_"))
def accept_handler(message):
    try:
        event_id = int(message.text.split("_")[1])

        participant_id = 1

        from events.models import EventParticipant, Event
        participant = EventParticipant.objects.get(
            event_id=event_id,
            user_id=participant_id
        )

        participant.status = "confirmed"
        participant.save()

        event = Event.objects.get(id=event_id)
        bot.reply_to(message, f"✅ Встреча '{event.name}' ПОДТВЕРЖДЕНА!\n📅 {event.date} {event.time}")

        stat = get_today_stats()
        stat.edited_events += 1
        stat.save()

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка подтверждения: {str(e)}")


@bot.message_handler(func=lambda m: m.text.startswith("/decline_"))
def decline_handler(message):  # ← параметр message
    try:
        event_id = int(message.text.split("_")[1])
        participant_id = 1

        from events.models import EventParticipant, Event
        participant = EventParticipant.objects.get(
            event_id=event_id,
            user_id=participant_id
        )

        participant.status = "cancelled"
        participant.save()

        event = Event.objects.get(id=event_id)
        bot.reply_to(message, f"❌ Встреча '{event.name}' ОТКЛОНЕНА\n📅 {event.date} {event.time}")

        stat = get_today_stats()
        stat.cancelled_events += 1
        stat.save()

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка отклонения: {str(e)}")


print("🚀 Бот с PostgreSQL запущен!")
bot.infinity_polling()
