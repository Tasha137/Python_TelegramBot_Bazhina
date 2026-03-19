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
from events.models import TelegramUser
from events.utils import get_user_events
import telebot.types as types

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
def decline_handler(message):
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


@bot.message_handler(commands=["login"])
def cmd_login(message):
    telegram_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    user, created = TelegramUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={'username': username, 'first_name': message.from_user.first_name}
    )

    if created:
        bot.reply_to(message, f"✅ Профиль создан!\n👤 @{username}\n🆔 {telegram_id}")
    else:
        user.username = username
        user.first_name = message.from_user.first_name
        user.save()
        bot.reply_to(message, f"✅ Профиль обновлён!\n👤 @{username}")


@bot.message_handler(commands=["calendar"])
def cmd_calendar(message):
    try:
        telegram_id = message.from_user.id
        events = get_user_events(telegram_id)

        if not events:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("➕ Создать", callback_data="add_mine"))
            bot.reply_to(message,
                         "📅 *У вас пока нет событий*\n\n"
                         "`/add_mine Встреча 2026-03-20 15:00 Описание`",
                         parse_mode='Markdown', reply_markup=markup)
            return

        text = f"📅 Ваш календарь ({len(events)}):\n\n"
        for i, event in enumerate(events, 1):
            date = event.get('date', '?')
            time = event.get('time', '?')
            name = event.get('name', 'Без названия')
            text += f"{i}. *{name}*\n   📅 `{date} {time}`\n"
            text += f"   /publish_{event['id']} | /unpublish_{event['id']}\n\n"

        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("➕ Добавить", callback_data="add_mine"),
            types.InlineKeyboardButton("📤 Публичные", callback_data="public")
        )

        bot.reply_to(message, text, parse_mode='Markdown', reply_markup=markup)

    except Exception as e:
        print(f"❌ CALENDAR ERROR: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")


@bot.message_handler(func=lambda m: m.text.startswith("/publish_"))
def publish_handler(message):
    """Делает событие публичным"""
    try:
        event_id = int(message.text.split("_")[1])
        from events.models import Event

        event = Event.objects.get(id=event_id)
        event.is_public = True
        event.save()

        bot.reply_to(message, f"✅ *{event.name}* теперь ПУБЛИЧНОЕ!\n"
                              f"📅 {event.date} {event.time}\n"
                              f"🔗 Другие смогут увидеть через /public_events")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")


@bot.message_handler(func=lambda m: m.text.startswith("/unpublish_"))
def unpublish_handler(message):
    """Делает событие приватным"""
    try:
        event_id = int(message.text.split("_")[1])
        from events.models import Event

        event = Event.objects.get(id=event_id)
        event.is_public = False
        event.save()

        bot.reply_to(message, f"🔒 *{event.name}* больше НЕ публичное")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

@bot.message_handler(commands=["debug_events"])
def cmd_debug_events(message):
    """DEBUG: показывает ВСЕ события и владельцев"""
    try:
        from events.models import Event, TelegramUser

        # Все пользователи
        users = list(TelegramUser.objects.all().values('id', 'username', 'telegram_id'))
        user_text = f"👥 Пользователи ({len(users)}):\n"
        for u in users:
            user_text += f"• ID:{u['id']} @{u['username']} (TG:{u['telegram_id']})\n"

        # Все события с владельцами
        events = Event.objects.all().values('id', 'name', 'owner_id')
        event_text = f"\n📅 События ({len(events)}):\n"
        for e in events:
            owner_id = e['owner_id']
            if owner_id:
                try:
                    owner = TelegramUser.objects.get(id=owner_id)
                    owner_name = f"@{owner.username}"
                except:
                    owner_name = f"ID:{owner_id} (удалён)"
            else:
                owner_name = "❌ БЕЗ ВЛАДЕЛЬЦА"
            event_text += f"• ID:{e['id']} {e['name']} (owner: {owner_name})\n"

        telegram_id = message.from_user.id
        my_events = Event.objects.filter(owner__telegram_id=telegram_id).count()
        event_text += f"\n💎 Твоих событий: {my_events}"

        bot.reply_to(message, f"{user_text}\n{event_text}")

    except Exception as e:
        bot.reply_to(message, f"❌ Debug ошибка: {str(e)}")


@bot.message_handler(commands=["public_events"])
def cmd_public_events(message):
    """Показывает публичные события всех пользователей"""
    try:
        from events.models import Event, TelegramUser

        public_events = Event.objects.filter(is_public=True).select_related('owner').order_by('date', 'time')[:10]

        if not public_events.exists():
            bot.reply_to(message, "🌐 Пока нет публичных событий\n\n"
                                  "👤 Опубликуйте своё: /publish_1")
            return

        text = "🌐 *ПУБЛИЧНЫЕ СОБЫТИЯ:*\n\n"
        for event in public_events:
            # ✅ БЕЗОПАСНО получаем owner
            owner_name = "Аноним"
            if event.owner_id:  # проверяем есть ли владелец
                try:
                    owner_name = event.owner.username or event.owner.first_name or "Пользователь"
                except:
                    owner_name = f"ID:{event.owner_id}"

            start = f"{event.date} {event.time}"
            text += f"• *{event.name}*\n  👤 @{owner_name} | 📅 {start}\n\n"

        bot.reply_to(message, text, parse_mode='Markdown')

    except Exception as e:
        print(f"❌ public_events: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

@bot.message_handler(commands=["add_mine"])
def cmd_add_mine(message):
    """Создаёт событие сразу привязанное к твоему профилю"""
    try:
        telegram_id = message.from_user.id
        args = message.text.split()[1:]
        if len(args) < 4:
            bot.reply_to(message, "❌ /add_mine <название> <дата> <время> <описание>")
            return

        from events.models import TelegramUser, Event

        # 1. Получаем пользователя
        user = TelegramUser.objects.get(telegram_id=telegram_id)

        # 2. Создаём событие БЕЗ owner сначала
        event = Event.objects.create(
            name=args[0],
            date=args[1],
            time=args[2],
            details=" ".join(args[3:])
        )

        # 3. ОБНОВЛЯЕМ owner ПОСЛЕ сохранения
        event.owner = user
        event.save()

        bot.reply_to(message, f"✅ *Твоё событие* `{event.name}` создано!\n📅 {event.date} {event.time}",
                     parse_mode='Markdown')

    except Exception as e:
        print(f"❌ add_mine: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

@bot.message_handler(commands=["test"])
def cmd_test(message):
    telegram_id = message.from_user.id
    from events.models import TelegramUser
    user = TelegramUser.objects.filter(telegram_id=telegram_id).first()

    if user:
        bot.reply_to(message, f"✅ Профиль: @{user.username} ID:{user.id}")
    else:
        bot.reply_to(message, f"❌ Профиль не найден для ID: {telegram_id}")


print("🚀 Бот с PostgreSQL запущен!")
bot.infinity_polling()


