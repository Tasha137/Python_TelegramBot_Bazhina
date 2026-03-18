from datetime import datetime
from .models import BotStatistics

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
