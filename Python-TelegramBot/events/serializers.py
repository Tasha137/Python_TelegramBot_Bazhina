from rest_framework import serializers
from .models import TelegramUser, Event


class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = "__all__"
        read_only_fields = ("created_at",)


class EventSerializer(serializers.ModelSerializer):
    owner = TelegramUserSerializer(read_only=True)  # или только id

    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ("created_at",)
