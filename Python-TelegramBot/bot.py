import telebot
from notes_service import create_note, read_note, edit_note, delete_note, display_notes, display_sorted_notes
from secrets import API_TOKEN

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
        "🗓️ *Календарь-Помощник*\n\n"
        "📝 *Команды:*\n"
        "/create <название> <текст>\n"
        "/read <название>\n"
        "/edit <название> <текст>\n"
        "/delete <название>\n"
        "/list\n"
        "/sort")

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
        bot.reply_to(message, "❌ Ошибка создания")

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
            bot.reply_to(message, text)
        else:
            bot.reply_to(message, "📭 Заметок нет")
    except:
        bot.reply_to(message, "❌ Ошибка списка")

@bot.message_handler(commands=['sort'])
def sort_notes_handler(message):
    try:
        success, notes = display_sorted_notes()
        if success and notes:
            text = "📋 *Отсортированные заметки:*\n" + "\n".join([f"• {note[:-4]}" for note in notes[:10]])
            bot.reply_to(message, text)
        else:
            bot.reply_to(message, "📭 Заметок нет")
    except:
        bot.reply_to(message, "❌ Ошибка сортировки")

print("🚀 Бот *Календарь-Помощник* запущен!")
bot.infinity_polling()
