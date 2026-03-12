import telebot
from notes_service import (create_note, read_note, edit_note, delete_note,
                          display_notes, display_sorted_notes, calendar)
from secrets import API_TOKEN

bot = telebot.TeleBot(API_TOKEN)

# ===== КОМАНДЫ ЗАМЕТОК =====
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
        """🗓️ Календарь-Помощник

📝 Заметки:
/create <название> <текст>
/read <название>
/edit <название> <текст>
/delete <название>
/list
/sort

📅 Календарь:
/calendar — меню
/create_event <название> <дата> <время> <описание>
/list_events
/read_event <ID>""")


@bot.message_handler(commands=['create'])
def create_note_handler(message):
    try:
        args = message.text.split()[1:]
        if len(args) < 2:
            bot.reply_to(message, "❌ /create <название> <текст>")
            return
        note_name = args[0]
        note_text = " ".join(args[1:])
        success, msg = create_note(note_name, note_text)
        bot.reply_to(message, msg)
    except:
        bot.reply_to(message, "❌ Ошибка создания заметки")

@bot.message_handler(commands=['read'])
def read_note_handler(message):
    try:
        args = message.text.split()[1:]
        if not args:
            bot.reply_to(message, "❌ /read <название>")
            return
        note_name = args[0]
        success, content = read_note(note_name)
        bot.reply_to(message, content)
    except:
        bot.reply_to(message, "❌ Ошибка чтения")

@bot.message_handler(commands=['edit'])
def edit_note_handler(message):
    try:
        args = message.text.split()[1:]
        if len(args) < 2:
            bot.reply_to(message, "❌ /edit <название> <текст>")
            return
        note_name = args[0]
        new_text = " ".join(args[1:])
        success, msg = edit_note(note_name, new_text)
        bot.reply_to(message, msg)
    except:
        bot.reply_to(message, "❌ Ошибка редактирования")

@bot.message_handler(commands=['delete'])
def delete_note_handler(message):
    try:
        args = message.text.split()[1:]
        if not args:
            bot.reply_to(message, "❌ /delete <название>")
            return
        note_name = args[0]
        success, msg = delete_note(note_name)
        bot.reply_to(message, msg)
    except:
        bot.reply_to(message, "❌ Ошибка удаления")

@bot.message_handler(commands=['list'])
def list_notes_handler(message):
    try:
        success, notes = display_notes()
        if success and notes:
            text = "📋 *Все заметки:*\n" + "\n".join([f"• {note[:-4]}" for note in notes[:10]])
            bot.reply_to(message, text, parse_mode='Markdown')
        else:
            bot.reply_to(message, "📭 Заметок нет")
    except:
        bot.reply_to(message, "❌ Ошибка списка")

@bot.message_handler(commands=['sort'])
def sort_notes_handler(message):
    try:
        success, notes = display_sorted_notes()
        if success and notes:
            text = "📋 *Отсортированные:*\n" + "\n".join([f"• {note[:-4]}" for note in notes[:10]])
            bot.reply_to(message, text, parse_mode='Markdown')
        else:
            bot.reply_to(message, "📭 Заметок нет")
    except:
        bot.reply_to(message, "❌ Ошибка сортировки")

# ===== КОМАНДЫ КАЛЕНДАРЯ =====
@bot.message_handler(commands=['calendar'])
def calendar_menu(message):
    bot.reply_to(message,
        """🗓️ КАЛЕНДАРЬ

📝 /create_event <название> <дата> <время> <описание>
📋 /list_events
👁 /read_event <ID>

Пример: /create_event Встреча 2026-03-15 14:00 тест""")

@bot.message_handler(commands=['create_event'])
def create_event_handler(message):
    try:
        args = message.text.split()[1:]
        if len(args) < 4:
            bot.reply_to(message,
                "❌ *Формат:* `/create_event <название> <дата> <время> <описание>`\n"
                "*Пример:* `/create_event Встреча 2026-03-15 14:00 Важная встреча`",
                parse_mode='Markdown')
            return
        event_name, event_date, event_time = args[0], args[1], args[2]
        event_details = " ".join(args[3:])
        success, msg = calendar.create_event(event_name, event_date, event_time, event_details)
        bot.reply_to(message, msg)
    except Exception as e:
        bot.reply_to(message, "❌ Ошибка создания события")

@bot.message_handler(commands=['list_events'])
def list_events_handler(message):
    try:
        success, text = calendar.list_events()
        bot.reply_to(message, text, parse_mode='Markdown')
    except:
        bot.reply_to(message, "❌ Нет событий")

@bot.message_handler(commands=['read_event'])
def read_event_handler(message):
    try:
        args = message.text.split()[1:]
        if not args:
            bot.reply_to(message, "❌ /read_event <ID>")
            return
        success, content = calendar.read_event(args[0])
        bot.reply_to(message, content, parse_mode='Markdown')
    except:
        bot.reply_to(message, "❌ Событие не найдено")

@bot.message_handler(commands=['calendar'])
def calendar_menu(message):
    bot.reply_to(message,
        """🗓️ КАЛЕНДАРЬ

📝 /create_event <название> <дата> <время> <описание>
📋 /list_events
👁 /read_event <ID>

Пример: /create_event Встреча 2026-03-15 14:00 тест""")

print("🚀 Бот *Календарь-Помощник* запущен!")
bot.infinity_polling()
