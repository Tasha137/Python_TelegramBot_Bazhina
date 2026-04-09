from unittest.mock import patch


@patch("bot.bot.send_message")
def test_send_notification(send_message):
    """Проверяет, что бот отправляет уведомление."""
    user_id = 123
    message_text = "Напоминание о событии."

    from bot import bot

    bot.send_message(user_id, message_text)

    send_message.assert_called_once_with(user_id, message_text)
