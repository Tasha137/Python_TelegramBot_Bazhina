# notes_service.py — ТОЛЬКО КАЛЕНДАРЬ (Задание №4)

class Calendar:
    def __init__(self):
        self.events = {}

    def create_event(self, event_name, event_date, event_time, event_details):
        event_id = len(self.events) + 1
        event = {
            "id": event_id,
            "name": event_name,
            "date": event_date,
            "time": event_time,
            "details": event_details
        }
        self.events[event_id] = event
        return True, f"✅ Событие '{event_name}' создано (ID: {event_id})"

    def read_event(self, event_id):
        try:
            event = self.events.get(int(event_id))
            if event:
                text = f"📅 *{event['name']}*\n🗓️ {event['date']} {event['time']}\n📝 {event['details']}"
                return True, text
            return False, "❌ Событие не найдено"
        except:
            return False, "❌ Неверный ID события"

    def list_events(self):
        if self.events:
            text = "📅 *Все события:*\n\n"
            for event_id, event in self.events.items():
                text += f"ID {event_id}: *{event['name']}* ({event['date']} {event['time']})\n"
            return True, text
        return True, "📭 Событий пока нет"


# Глобальный объект календаря
calendar = Calendar()
