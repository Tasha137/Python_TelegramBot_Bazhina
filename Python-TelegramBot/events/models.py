from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Event(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_events")
    name = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    details = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('TelegramUser', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='owned_events')
    is_public = models.BooleanField(default=False, verbose_name="Публичное")

    def __str__(self):
        return f"{self.owner.username} - {self.name} - {self.date} - {self.time}"

class EventParticipant(models.Model):
    STATUS_CHOICES = [
        ("pending", "Ожидание"),
        ("confirmed", "Подтверждено"),
        ("cancelled", "Отменено"),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="event_participations")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    class Meta:
        unique_together = ("event", "user")

    def __str__(self):
        return f"{self.user.username} - {self.event.name} ({self.status})"


class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    username = models.CharField(max_length=100, blank=True, verbose_name="Username")
    first_name = models.CharField(max_length=100, blank=True, verbose_name="Имя")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Telegram пользователь"
        verbose_name_plural = "Telegram пользователи"

    def __str__(self):
        return f"@{self.username or self.first_name} (ID: {self.telegram_id})"


Event.owner = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='owned_events', null=True,
                                blank=True, verbose_name="Владелец")


class BotStatistics(models.Model):
    date = models.DateField()
    user_count = models.PositiveIntegerField()
    event_count = models.PositiveIntegerField()
    edited_events = models.PositiveIntegerField()
    cancelled_events = models.PositiveIntegerField()

    def __str__(self):
        return f"Статистика за {self.date}"


class UserStatistics(models.Model):
    user = models.OneToOneField(TelegramUser, on_delete=models.CASCADE, related_name='stats')
    created_events = models.IntegerField(default=0)
    edited_events = models.IntegerField(default=0)
    cancelled_events = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Статистика пользователя"
        verbose_name_plural = "Статистика пользователей"

    def __str__(self):
        return f"Статистика @{self.user.username}"


