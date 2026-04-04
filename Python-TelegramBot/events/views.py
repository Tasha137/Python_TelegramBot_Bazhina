import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from .models import TelegramUser, Event

def export_events_csv(request):
    telegram_id = request.GET.get("telegram_id")
    if not telegram_id:
        return HttpResponse("Не указан telegram_id", status=400)

    try:
        tg_user = TelegramUser.objects.get(telegram_id=telegram_id)
    except TelegramUser.DoesNotExist:
        return HttpResponse("Профиль Telegram не найден", status=404)

    events = tg_user.owned_events.all()

    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = f'attachment; filename="events_{tg_user.telegram_id}.csv"'

    writer = csv.writer(response)
    writer.writerow(["Название", "Дата", "Время", "Детали", "Публичное?"])

    for event in events:
        writer.writerow([
            event.name,
            event.date,
            event.time,
            event.details or "",
            "Да" if event.is_public else "Нет",
        ])

    return response