from os import environ

DB_HOST = "db"
DB_PORT = 5432
DB_NAME = "calendar_db"
DB_USER = "calendar_user"
DB_PASSWORD = "calendar_pass"

API_TOKEN = environ.get("8634765574:AAEalcIcbAaYTRiIGKF7tftZxMTER_8rrPI")
if API_TOKEN is None:
    API_TOKEN = "8634765574:AAEalcIcbAaYTRiIGKF7tftZxMTER_8rrPI"

HOST = "http://web"
PORT = 8000
SECRET_KEY = "your_django_secret_key"