from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

from events import views


def index(request):
    return HttpResponse(
        "Главная страница бота. "
        "Перейдите на /calendar/export/events/csv/ для выгрузки событий."
    )


urlpatterns = [
    path(
        "calendar/export/events/csv/",
        views.export_events_csv,
        name="export_events_csv"
    ),
    path("admin/", admin.site.urls),
    path("", include("events.urls")),
    path("", include("events.urls_api")),
]
