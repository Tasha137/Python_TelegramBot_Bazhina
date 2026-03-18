from django.contrib import admin
from .models import BotStatistics, Event

@admin.register(BotStatistics)
class BotStatisticsAdmin(admin.ModelAdmin):
    list_display = ("date", "user_count", "event_count", "edited_events", "cancelled_events")
    list_filter = ("date",)
    ordering = ("-date",)
