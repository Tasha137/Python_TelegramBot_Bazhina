from datetime import datetime, timedelta
from .models import EventParticipant, BotStatistics, TelegramUser, Event


def get_user_busy_intervals(user):
    """Получить занятые интервалы пользователя"""
    participations = EventParticipant.objects.filter(
        user=user,
        status__in=["pending", "confirmed"],
    ).select_related("event")

    intervals = []
    for p in participations:
        start = datetime.combine(p.event.date, p.event.time)
        end = start + timedelta(hours=1)  # встреча 1 час
        intervals.append((start, end))
    return intervals


def get_today_stats():
    today = datetime.now().date()
    stat, created = BotStatistics.objects.get_or_create(
        date=today,
        defaults={
            "user_count": 0,
            "event_count": 0,
            "edited_events": 0,
            "cancelled_events": 0,
        },
    )
    return stat


def is_user_free(user, event_date, event_time, duration_hours=1):
    """Проверить, свободен ли пользователь в дату/время"""
    new_start = datetime.combine(event_date, event_time)
    new_end = new_start + timedelta(hours=duration_hours)

    busy_intervals = get_user_busy_intervals(user)
    for busy_start, busy_end in busy_intervals:
        if not (new_end <= busy_start or new_start >= busy_end):
            return (
                False,
                f"Занят: {busy_start.strftime('%H:%M')} - "
                f"{busy_end.strftime('%H:%M')}",
            )
    return True, "Свободен"


def get_user_events(telegram_id: int) -> list:
    """Возвращает события пользователя по ТВОИМ полям модели"""
    try:
        user = TelegramUser.objects.get(telegram_id=telegram_id)
        events = Event.objects.filter(owner=user).values(
            "id", "name", "date", "time", "details", "is_public"
        )[:10]

        return list(events)

    except TelegramUser.DoesNotExist:
        print(f"🔍 Пользователь {telegram_id} не найден")  # ДИАГНОСТИКА
        return []

    except Exception as e:
        print(f"❌ Ошибка get_user_events: {e}")  # ДИАГНОСТИКА
        return []
