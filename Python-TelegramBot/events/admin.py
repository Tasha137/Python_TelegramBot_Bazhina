from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from django.utils import timezone
from .models import Event, TelegramUser, EventParticipant, Stats


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'time', 'owner', 'is_public', 'participant_count']
    list_filter = ['date', 'is_public', 'owner', 'created_at']
    search_fields = ['name', 'details']
    readonly_fields = ['participant_count']

    def participant_count(self, obj):
        count = obj.eventparticipant_set.count()
        return format_html('<span style="color: green;">{}</span>', count)
    participant_count.short_description = 'Участников'


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'telegram_id', 'event_count']
    search_fields = ['username', 'telegram_id', 'first_name']

    def event_count(self, obj):
        count = obj.event_set.count()
        return format_html('<span style="color: blue;">{}</span>', count)
    event_count.short_description = 'Событий'


class StatsAdmin(admin.ModelAdmin):
    list_display = ['date', 'user_count', 'event_count', 'edited_events', 'cancelled_events']
    list_filter = ['date']
    readonly_fields = ['date', 'user_count', 'event_count', 'edited_events', 'cancelled_events']

    def has_add_permission(self, request):
        return False  # Только просмотр

    def changelist_view(self, request, extra_context=None):
        # Сегодняшняя статистика
        today = timezone.now().date()
        stats, created = Stats.objects.get_or_create(date=today)
        extra_context = extra_context or {}
        extra_context['today_stats'] = stats
        return super().changelist_view(request, extra_context=extra_context)


admin.site.register(Stats, StatsAdmin)
admin.site.register(EventParticipant)
