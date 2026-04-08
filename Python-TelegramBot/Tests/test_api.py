import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from events.models import TelegramUser

from rest_framework.authtoken.models import Token

@pytest.mark.django_db
def test_create_event_api_ok():
    client = APIClient()

    # 1. Создаём пользователя и токен
    user = User.objects.create_user(username="testuser", password="testpass")
    token = Token.objects.create(user=user)

    # 2. Авторизуем клиент
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    # 3. Создаём TelegramUser
    TelegramUser.objects.create(telegram_id=123)

    # 4. Запрос к API
    url = reverse("event-list")
    data = {
        "name": "Test API Event",
        "user_id": 123,
        "date": "2026-04-06",
        "time": "10:00:00",
    }

    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_event_api_bad_request():
    client = APIClient()

    user = User.objects.create_user(username="testuser", password="testpass")
    token = Token.objects.create(user=user)

    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    TelegramUser.objects.create(telegram_id=123)

    url = reverse("event-list")
    data = {
        "name": "Event без даты",
        "user_id": 123,
        "time": "10:00:00",
    }

    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST