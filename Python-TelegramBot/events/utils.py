from django.utils import timezone
from .models import Stats, Event, TelegramUser


def get_today_stats():
    today = timezone.now().date()
    stats, created = Stats.objects.get_or_create(date=today)
    return stats


def get_user_events(telegram_id):
    try:
        user = TelegramUser.objects.get(telegram_id=telegram_id)
        return list(user.event_set.values('id', 'name', 'date', 'time'))
    except TelegramUser.DoesNotExist:
        return []
