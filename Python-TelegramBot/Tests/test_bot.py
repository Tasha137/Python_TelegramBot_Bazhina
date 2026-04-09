from unittest.mock import Mock, patch

from bot_minimal import bot, handle_start, handle_login, handle_help


def test_start_command():
    message = Mock()
    message.text = "/start"
    message.chat.id = 123

    with patch.object(bot, "reply_to") as reply_to:
        handle_start(message)
        reply_to.assert_called_once()
        args, _ = reply_to.call_args
        assert "Бот живёт" in args[1]


def test_login_command():
    message = Mock()
    message.text = "/login"
    message.chat.id = 123

    with patch.object(bot, "reply_to") as reply_to:
        handle_login(message)
        reply_to.assert_called_once()


def test_help_command():
    message = Mock()
    message.text = "/help"
    message.chat.id = 123

    with patch.object(bot, "reply_to") as reply_to:
        handle_help(message)
        reply_to.assert_called_once()
