import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calendar_admin.settings')
import django
django.setup()

import shlex
import logging
from datetime import datetime, timedelta

import telebot
import telebot.types as types
import urllib3

from secrets_bot import API_TOKEN
import telegram_calendar

from events.models import TelegramUser, Event, EventParticipant
from events.utils import get_today_stats, get_user_events

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ["PYTHONWARNINGS"] = "ignore::urllib3.exceptions.InsecureRequestWarning"
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

telebot.apihelper.REQUEST_TIMEOUT = 30
telebot.apihelper.LONG_POLLING_TIMEOUT = 20

bot = telebot.TeleBot(API_TOKEN)
calendar = telegram_calendar.Calendar()


def parse_args(message_text: str):
    try:
        return shlex.split(message_text)
    except ValueError:
        return None


@bot.message_handler(commands=["start"])
def start(message):
    """
    Регистрирует пользователя в базе и показывает главное меню бота.
    """
    # Берём данные пользователя из Telegram.
    telegram_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    # Создаём профиль, если пользователь запускает бота впервые.
    user, created = TelegramUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            "username": username,
            "first_name": message.from_user.first_name,
        },
    )

    # Обновляем имя и username, если профиль уже существует.
    if not created:
        user.username = username
        user.first_name = message.from_user.first_name
        user.save()

    # Отправляем список доступных команд.
    bot.reply_to(
        message,
        "🗓️ Календарь-Помощник (PostgreSQL)\n"
        "📅 Календарь:\n"
        "/add_main <название> <дата> <время> <описание>\n"
        "/list_events\n"
        "/read_event <название>\n"
        "/edit_event <название> <новая_дата> <новое_описание>\n"
        "/delete_event <название>\n"
        "/Пример: /create_event Встреча 2026-03-15 14:00 текст",
    )

    # Обновляем статистику запусков.
    stat = get_today_stats()
    stat.user_count += 1
    stat.save()


@bot.message_handler(commands=["create_event"])
def create_event_handler(message):
    """
    Создаёт событие через календарный модуль и сохраняет его в базе.
    """
    try:
        # Разбираем аргументы команды.
        parts = parse_args(message.text)
        if not parts or len(parts) < 5:
            bot.reply_to(
                message,
                "❌ /create_event <название> <дата> <время> <описание>",
            )
            return

        # Извлекаем параметры события.
        event_name = parts[1]
        event_date = parts[2]
        event_time = parts[3]
        details = " ".join(parts[4:])
        user_id = message.from_user.id

        # Формируем время начала и окончания.
        start_time = f"{event_date} {event_time}"
        dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        end_time = (dt + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")

        # Сохраняем событие.
        try:
            event_id = calendar.add_event(
                name=event_name,
                start_time=start_time,
                end_time=end_time,
                user_id=user_id,
            )
            bot.reply_to(message, f"✅ Событие '{event_name}' создано! ID: {event_id}")
        except Exception as e:
            bot.reply_to(message, f"❌ Ошибка записи в БД: {e}")

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка обработки команды: {e}")


@bot.message_handler(commands=["add_main"])
def add_main_handler(message):
    """
    Создаёт основное событие календаря по названию, дате, времени и описанию.
    """
    try:
        # Разбираем аргументы команды.
        parts = parse_args(message.text)
        if not parts or len(parts) < 5:
            bot.reply_to(
                message,
                '❌ /add_main "название" YYYY-MM-DD HH:MM "описание"',
            )
            return

        # Извлекаем параметры события.
        title = parts[1]
        event_date = parts[2]
        event_time = parts[3]
        description = " ".join(parts[4:])
        user_id = message.from_user.id

        # Формируем время начала и окончания.
        start_time = f"{event_date} {event_time}"
        dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        end_time = (dt + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")

        # Сохраняем событие.
        try:
            event_id = calendar.add_event(
                name=title,
                start_time=start_time,
                end_time=end_time,
                user_id=user_id,
            )
            bot.reply_to(message, f"✅ Событие '{title}' создано! ID: {event_id}")
        except Exception as e:
            bot.reply_to(message, f"❌ Ошибка записи в БД: {e}")

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка обработки команды: {e}")


@bot.message_handler(commands=["list_events"])
def list_events_handler(message):
    """
    Показывает список всех событий прямо в Telegram.
    """
    try:
        events = list(Event.objects.all().order_by("date", "time"))

        if not events:
            bot.reply_to(message, "📭 Событий пока нет")
            return

        text = f"📅 События ({len(events)}):\n\n"
        for i, event in enumerate(events, 1):
            text += (
                f"{i}. {event.name}\n"
                f"   📅 {event.date} {event.time}\n"
            )
            if hasattr(event, "description") and event.description:
                text += f"   📝 {event.description}\n"
            text += "\n"

        bot.reply_to(message, text)

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")


@bot.message_handler(commands=["read_event"])
def read_event_handler(message):
    """
    Ищет событие по названию и выводит его данные в Telegram.
    """
    try:
        # Разбираем аргументы команды.
        parts = parse_args(message.text)
        if not parts or len(parts) < 2:
            bot.reply_to(message, "❌ /read_event <название>")
            return

        event_name = " ".join(parts[1:]).strip()
        event = Event.objects.filter(name__iexact=event_name).first()

        if not event:
            bot.reply_to(message, "❌ Событие не найдено")
            return

        text = (
            f"✅ Найдено событие:\n"
            f"📌 {event.name}\n"
            f"📅 {event.date} {event.time}"
        )

        if hasattr(event, "description") and event.description:
            text += f"\n📝 {event.description}"

        bot.reply_to(message, text)

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")


@bot.message_handler(commands=["edit_event"])
def edit_event_handler(message):
    """
    Обновляет дату и описание события по его названию.
    """
    try:
        # Разбираем аргументы команды.
        parts = parse_args(message.text)
        if not parts or len(parts) < 4:
            bot.reply_to(
                message,
                '❌ /edit_event "название" <новая_дата> <новое_описание>',
            )
            return

        # Получаем новые значения.
        event_name = parts[1]
        new_date = parts[2]
        new_details = " ".join(parts[3:])

        # Обновляем событие.
        if calendar.edit_event(
            event_name,
            new_date,
            new_description=new_details,
        ):
            bot.reply_to(message, f"✅ Событие '{event_name}' обновлено!")
        else:
            bot.reply_to(message, "❌ Событие не найдено")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

    # Обновляем статистику редактирования.
    stat = get_today_stats()
    stat.event_count += 1
    stat.save()


@bot.message_handler(commands=["delete_event"])
def delete_event_handler(message):
    """
    Удаляет событие по названию из календаря.
    """
    try:
        # Разбираем аргументы команды.
        parts = parse_args(message.text)
        if not parts or len(parts) < 2:
            bot.reply_to(message, "❌ /delete_event <название>")
            return

        # Собираем название события.
        event_name = " ".join(parts[1:])

        # Удаляем событие.
        if calendar.delete_event(event_name):
            bot.reply_to(message, f"✅ Событие '{event_name}' удалено из PostgreSQL!")
        else:
            bot.reply_to(message, "❌ Событие не найдено")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

    # Обновляем статистику удаления.
    stat = get_today_stats()
    stat.event_count += 1
    stat.save()


@bot.message_handler(commands=["invite"])
def invite_handler(message):
    """
    Приглашает пользователя в событие по username.
    """
    try:
        # Разбираем команду на части: /invite, @username, название события.
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            bot.reply_to(
                message,
                "❌ Формат: /invite @username <название_события>"
            )
            return

        # Получаем username и название события.
        username = parts[1].lstrip("@")
        event_name = parts[2].strip()

        # Ищем событие в базе.
        event = Event.objects.filter(name__iexact=event_name).first()
        if not event:
            bot.reply_to(message, f"❌ Событие '{event_name}' не найдено")
            return

        # Ищем пользователя TelegramUser по username.
        target_user = TelegramUser.objects.filter(username=username).first()
        if not target_user:
            bot.reply_to(message, f"❌ Пользователь @{username} не найден в базе")
            return

        # Создаём запись участия в событии для реального telegram_id.
        participant, created = EventParticipant.objects.get_or_create(
            event=event,
            user_id=target_user.telegram_id,
            defaults={"status": "pending"},
        )

        # Сообщаем результат приглашения.
        if created:
            bot.reply_to(
                message,
                f"✅ Приглашение отправлено @{username} на событие '{event.name}'"
            )
        else:
            bot.reply_to(
                message,
                f"ℹ️ @{username} уже добавлен в событие '{event.name}'"
            )

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка при приглашении: {e}")


@bot.message_handler(func=lambda m: m.text and m.text.startswith("/accept_"))
def accept_handler(message):
    """
    Подтверждает участие пользователя в событии.
    """
    try:
        # Получаем ID события из команды.
        event_id = int(message.text.split("_")[1])

        # Берём реальный Telegram ID пользователя.
        telegram_id = message.from_user.id

        # Ищем именно его приглашение.
        participant = EventParticipant.objects.get(
            event_id=event_id,
            user_id=telegram_id,
        )
        participant.status = "confirmed"
        participant.save()

        # Получаем событие для ответа пользователю.
        event = Event.objects.get(id=event_id)
        bot.reply_to(
            message,
            f"✅ Встреча '{event.name}' ПОДТВЕРЖДЕНА!\n📅 {event.date} {event.time}",
        )

        # Обновляем статистику подтверждений.
        stat = get_today_stats()
        stat.edited_events += 1
        stat.save()

    except EventParticipant.DoesNotExist:
        bot.reply_to(message, "❌ Для вас не найдено приглашение на это событие")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка подтверждения: {str(e)}")


@bot.message_handler(func=lambda m: m.text and m.text.startswith("/decline_"))
def decline_handler(message):
    """
    Отклоняет участие пользователя в событии.
    """
    try:
        # Получаем ID события из команды.
        event_id = int(message.text.split("_")[1])

        # Берём реальный Telegram ID пользователя.
        telegram_id = message.from_user.id

        # Ищем именно его приглашение.
        participant = EventParticipant.objects.get(
            event_id=event_id,
            user_id=telegram_id,
        )
        participant.status = "cancelled"
        participant.save()

        # Получаем событие для ответа пользователю.
        event = Event.objects.get(id=event_id)
        bot.reply_to(
            message,
            f"❌ Встреча '{event.name}' ОТКЛОНЕНА\n📅 {event.date} {event.time}",
        )

        # Обновляем статистику отклонений.
        stat = get_today_stats()
        stat.cancelled_events += 1
        stat.save()

    except EventParticipant.DoesNotExist:
        bot.reply_to(message, "❌ Для вас не найдено приглашение на это событие")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка отклонения: {str(e)}")

@bot.message_handler(commands=["login"])
def cmd_login(message):
    """
    Сообщает, что регистрация пользователя выполняется автоматически через /start.
    """
    bot.reply_to(message, "ℹ️ Пользователь регистрируется автоматически через /start")


@bot.message_handler(commands=["calendar"])
def cmd_calendar(message):
    """
    Показывает список событий пользователя и кнопки для дальнейших действий.
    """
    try:
        # Получаем события текущего пользователя.
        telegram_id = message.from_user.id
        events = get_user_events(telegram_id)

        # Если событий нет, показываем подсказку и кнопку создания.
        if not events:
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("➕ Создать", callback_data="add_mine")
            )
            bot.reply_to(
                message,
                "📅 *У вас пока нет событий*\n\n"
                "`/add_mine Встреча 2026-03-20 15:00 Описание`",
                reply_markup=markup,
            )
            return

        # Формируем текст со списком событий.
        text = f"📅 Ваш календарь ({len(events)}):\n\n"
        for i, event in enumerate(events, 1):
            date = event.get("date", "?")
            time = event.get("time", "?")
            name = event.get("name", "Без названия")
            text += f"{i}. {name}\n   📅 {date} {time}\n"
            text += f"   /publish_{event['id']} | /unpublish_{event['id']}\n\n"

        # Добавляем кнопки действий.
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("➕ Добавить", callback_data="add_mine"),
            types.InlineKeyboardButton("📤 Публичные", callback_data="public"),
        )

        bot.reply_to(message, text, reply_markup=markup)

    except Exception as e:
        print(f"❌ CALENDAR ERROR: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")


@bot.message_handler(func=lambda m: m.text and m.text.startswith("/publish_"))
def publish_handler(message):
    """
    Делает событие публичным.
    """
    try:
        # Получаем ID события.
        event_id = int(message.text.split("_")[1])
        event = Event.objects.get(id=event_id)

        # Меняем статус события.
        event.is_public = True
        event.save()

        # Сообщаем результат.
        bot.reply_to(
            message,
            f"✅ {event.name} теперь ПУБЛИЧНОЕ!\n"
            f"📅 {event.date} {event.time}\n"
            f"🔗 Другие смогут увидеть через /public_events",
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")


@bot.message_handler(func=lambda m: m.text and m.text.startswith("/unpublish_"))
def unpublish_handler(message):
    """
    Скрывает событие из публичного списка.
    """
    try:
        # Получаем ID события.
        event_id = int(message.text.split("_")[1])
        event = Event.objects.get(id=event_id)

        # Снимаем флаг публичности.
        event.is_public = False
        event.save()

        bot.reply_to(message, f"🔒 {event.name} больше НЕ публичное")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")


@bot.message_handler(commands=["debug_events"])
def cmd_debug_events(message):
    """
    Выводит отладочную информацию о пользователях и событиях.
    """
    try:
        # Собираем список пользователей.
        users = list(TelegramUser.objects.all().values("id", "username", "telegram_id"))
        user_text = f"👥 Пользователи ({len(users)}):\n"
        for u in users:
            user_text += f"• ID:{u['id']} @{u['username']} (TG:{u['telegram_id']})\n"

        # Собираем список событий.
        events = list(Event.objects.all().values("id", "name", "owner_id"))
        event_text = f"\n📅 События ({len(events)}):\n"
        for e in events:
            owner_id = e["owner_id"]
            if owner_id:
                try:
                    owner = TelegramUser.objects.get(id=owner_id)
                    owner_name = f"@{owner.username}"
                except:
                    owner_name = f"ID:{owner_id} (удалён)"
            else:
                owner_name = "❌ БЕЗ ВЛАДЕЛЬЦА"
            event_text += f"• ID:{e['id']} {e['name']} (owner: {owner_name})\n"

        # Считаем количество событий текущего пользователя.
        telegram_id = message.from_user.id
        my_events = Event.objects.filter(owner__telegram_id=telegram_id).count()
        event_text += f"\n💎 Твоих событий: {my_events}"

        bot.reply_to(message, f"{user_text}\n{event_text}")

    except Exception as e:
        bot.reply_to(message, f"❌ Debug ошибка: {str(e)}")


@bot.message_handler(commands=["public_events"])
def cmd_public_events(message):
    """
    Показывает список публичных событий.
    """
    try:
        # Берём только публичные события.
        public_events = (
            Event.objects.filter(is_public=True)
            .select_related("owner")
            .order_by("date", "time")[:10]
        )

        # Если публичных событий нет, показываем подсказку.
        if not public_events.exists():
            bot.reply_to(
                message,
                "🌐 Пока нет публичных событий\n\n"
                "👤 Опубликуйте своё: /publish_1",
            )
            return

        # Формируем текст списка публичных событий.
        text = "🌐 *ПУБЛИЧНЫЕ СОБЫТИЯ:*\n\n"
        for event in public_events:
            owner_name = "Аноним"
            if event.owner_id:
                try:
                    owner_name = event.owner.username or event.owner.first_name or "Пользователь"
                except:
                    owner_name = f"ID:{event.owner_id}"

            start = f"{event.date} {event.time}"
            text += f"• {event.name}\n  👤 {owner_name} | 📅 {start}\n\n"

        bot.reply_to(message, text)

    except Exception as e:
        print(f"❌ public_events: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")


@bot.message_handler(commands=["add_mine"])
def add_main_handler(message):
    """
    Создаёт личное событие пользователя.
    """
    # Разбираем аргументы команды.
    parts = message.text.split()
    if len(parts) < 5:
        return bot.reply_to(message, "❌ /add_main <название> <дата> <время> <описание>")

    # Извлекаем параметры события.
    name = parts[1]
    date = parts[2]
    time = parts[3]
    user_id = message.from_user.id

    # Формируем время начала и окончания.
    start_time = f"{date} {time}"
    dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
    end_time = (dt + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")

    # Сохраняем событие.
    event_id = calendar.add_event(name, start_time, end_time, user_id)
    bot.reply_to(message, f"✅ Событие '{name}' создано! ID: {event_id}")


@bot.message_handler(commands=["test"])
def cmd_test(message):
    """
    Проверяет, есть ли профиль Telegram-пользователя в базе.
    """
    # Ищем пользователя по telegram_id.
    telegram_id = message.from_user.id
    user = TelegramUser.objects.filter(telegram_id=telegram_id).first()

    # Сообщаем результат проверки.
    if user:
        bot.reply_to(message, f"✅ Профиль: @{user.username} ID:{user.id}")
    else:
        bot.reply_to(message, f"❌ Профиль не найден для ID: {telegram_id}")


@bot.message_handler(commands=["export_events"])
def cmd_export_events(message):
    """
    Отправляет пользователю ссылку для скачивания его событий в CSV.
    """
    # Проверяем, есть ли профиль в базе.
    telegram_id = message.from_user.id
    user = TelegramUser.objects.filter(telegram_id=telegram_id).first()

    if not user:
        bot.reply_to(message, "❌ Сначала выполните /login")
        return

    # Формируем ссылку на экспорт.
    download_url = (
        f"http://127.0.0.1:8000/calendar/export/events/csv/?telegram_id={telegram_id}"
    )

    # Отправляем кнопку скачивания.
    bot.reply_to(
        message,
        "Скачать свои события:",
        reply_markup=types.InlineKeyboardMarkup(
            [[types.InlineKeyboardButton("📤 Скачать CSV", url=download_url)]]
        ),
    )


print("🚀 Бот с PostgreSQL запущен!")
bot.polling(none_stop=True, interval=0)
