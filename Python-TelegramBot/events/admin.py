from django.contrib import admin
from .models import BotStatistics, Event, EventParticipant
from .models import TelegramUser

@admin.register(BotStatistics)
class BotStatisticsAdmin(admin.ModelAdmin):
    list_display = ("date", "user_count", "event_count", "edited_events", "cancelled_events")
    list_filter = ("date",)
    ordering = ("-date",)

@admin.register(Event)  # ← ДОБАВИТЬ ЭТО!
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'time', 'owner')
    list_filter = ('date', 'owner')
    search_fields = ('name',)

@admin.register(EventParticipant)  # ← Уже должно быть
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ("event", "user", "status")
    list_filter = ("status", "event__date")
    search_fields = ("event__name", "user__username")

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'telegram_id', 'first_name', 'created_at', 'events_count']
    list_filter = ['created_at']
    search_fields = ['telegram_id', 'username', 'first_name']

    def events_count(self, obj):
        return obj.owned_events.count()

    events_count.short_description = 'Событий'