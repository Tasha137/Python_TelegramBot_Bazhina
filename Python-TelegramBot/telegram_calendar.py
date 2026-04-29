import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calendar_admin.settings')
import django
django.setup()

from events.models import Event, TelegramUser
from datetime import datetime, timedelta


class Calendar:
    def __init__(self):
        pass

    def add_event(self, name, start_time, end_time, user_id):
        try:
            user, _ = TelegramUser.objects.get_or_create(telegram_id=user_id)
            event = Event.objects.create(
                name=name,
                date=datetime.strptime(start_time, "%Y-%m-%d %H:%M").date(),
                time=datetime.strptime(start_time, "%Y-%m-%d %H:%M").time(),
                owner=user,
            )
            return event.id
        except Exception as e:
            print(f"Error adding event: {e}")
            return None

    def get_events(self):
        return list(Event.objects.values('id', 'name', 'date', 'time', 'owner__telegram_id'))

    def display_events(self):
        events = self.get_events()
        print("📅 Все события:")
        for event in events:
            print(f"  ID: {event['id']}, {event['name']} ({event['date']} {event['time']})")

    def read_event(self, name):
        return list(Event.objects.filter(name__icontains=name).values())

    def delete_event(self, name):
        count = Event.objects.filter(name__icontains=name).delete()[0]
        return count > 0

    def edit_event(self, name, new_date_str, new_description=""):
        events = Event.objects.filter(name__icontains=name)
        if not events.exists():
            return False
        event = events.first()
        event.date = datetime.strptime(new_date_str, "%Y-%m-%d").date()
        event.details = new_description
        event.save()
        return True
