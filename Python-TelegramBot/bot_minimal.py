import telebot
from secrets_bot import API_TOKEN


bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.reply_to(message, "Бот живёт.")


def start_bot():
    bot.infinity_polling()


@bot.message_handler(commands=["login"])
def handle_login(message):
    bot.reply_to(message, "Пользователь вошёл.")


@bot.message_handler(commands=["help"])
def handle_help(message):
    bot.reply_to(message, "Доступны команды: /start, /login, /help.")
