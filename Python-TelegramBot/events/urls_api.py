from django.urls import path
from .views import EventListCreateAPIView, EventDetailAPIView

urlpatterns = [
    path("api/events/", EventListCreateAPIView.as_view(), name="event-list"),
    path("api/events/<int:pk>/", EventDetailAPIView.as_view(), name="event-detail"),  # noqa: E501
]
