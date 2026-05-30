import os
import requests

TOKEN = os.environ.get("DRF_TOKEN")
EVENTS_URL = "http://127.0.0.1:8000/api/events/"

if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("DRF_TOKEN is not set in environment variables")

    headers = {"Authorization": f"Token {TOKEN}"}
    data = {
        "name": "Test API Event",
        "user_id": 123,
        "date": "2026-04-06",
        "time": "10:00:00",
    }

    print("URL:", EVENTS_URL)
    print("HEADERS:", headers)
    print("BODY:", data)

    response = requests.post(EVENTS_URL, json=data, headers=headers)
    print("STATUS  :", response.status_code)
    print("RESPONSE:", response.text)
