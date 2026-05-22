from django.db import models
from django.contrib.auth.models import User


class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"@{self.username or self.first_name} ({self.telegram_id})"


class Event(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    details = models.TextField(blank=True)
    owner = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, null=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.name} ({self.date} {self.time})"


class EventParticipant(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидание'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отклонено'),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user_id = models.BigIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    invited_at = models.DateTimeField(auto_now_add=True)


class Stats(models.Model):
    date = models.DateField()
    user_count = models.IntegerField(default=0)
    event_count = models.IntegerField(default=0)
    edited_events = models.IntegerField(default=0)
    cancelled_events = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Статистика"
