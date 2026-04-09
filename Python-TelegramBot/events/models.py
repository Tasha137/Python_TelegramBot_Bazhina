from django.db import models
from django.contrib.auth.models import User
import secrets


class TelegramUser(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="telegramuser",
        blank=True,
        null=True,
        verbose_name="Django User",
    )
    telegram_id = models.BigIntegerField(
        unique=True,
        verbose_name="Telegram ID"
    )
    username = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Username"
    )
    first_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Имя"
    )
    export_token = models.CharField(
        max_length=64,
        unique=True,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.export_token:
            self.export_token = secrets.token_hex(16)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"@{self.username or self.first_name} (ID: {self.telegram_id})"


class TelegramUserMeta:
    class Meta:
        verbose_name = "Telegram пользователь"
        verbose_name_plural = "Telegram пользователи"


class Event(models.Model):
    owner = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name="owned_events",
        null=True,
        blank=True,
        verbose_name="Владелец",
    )
    name = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    details = models.TextField(null=True, blank=True)
    is_public = models.BooleanField(default=False, verbose_name="Публичное")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.owner:
            return f"Event '{self.name}' (owner: @{self.owner.username})"
        return f"Event '{self.name}' (no owner)"


class EventParticipant(models.Model):
    STATUS_CHOICES = [
        ("pending", "Ожидание"),
        ("confirmed", "Подтверждено"),
        ("cancelled", "Отменено"),
    ]

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="participants"
    )
    user_id = models.BigIntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending"
    )

    class Meta:
        unique_together = ("event", "user_id")

    def __str__(self):
        return f"User {self.user_id} - {self.event.name} ({self.status})"


class BotStatistics(models.Model):
    date = models.DateField()
    user_count = models.PositiveIntegerField()
    event_count = models.PositiveIntegerField()
    edited_events = models.PositiveIntegerField()
    cancelled_events = models.PositiveIntegerField()

    def __str__(self):
        return f"Статистика за {self.date}"


class UserStatistics(models.Model):
    user = models.OneToOneField(
        TelegramUser, on_delete=models.CASCADE, related_name="stats"
    )
    created_events = models.IntegerField(default=0)
    edited_events = models.IntegerField(default=0)
    cancelled_events = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
