from django.db import models

class Event(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    details = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.date} {self.time}"

    class Meta:
        ordering = ['date', 'time']

class BotStatistics(models.Model):
    date = models.DateField()
    user_count = models.PositiveIntegerField()
    event_count = models.PositiveIntegerField()
    edited_events = models.PositiveIntegerField()
    cancelled_events = models.PositiveIntegerField()

    def __str__(self):
        return f"Статистика за {self.date}"




