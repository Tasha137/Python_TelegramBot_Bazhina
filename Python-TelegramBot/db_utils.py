import psycopg2
from psycopg2 import OperationalError
import time

DB_HOST = "127.0.0.1"
DB_PORT = 5432
DB_NAME = "calendar_db"
DB_USER = "calendar_user"
DB_PASSWORD = "calendar_pass"


def get_db_connection():
    """Получаем подключение к PostgreSQL, ждём, если БД стартует."""
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            print("✅ База данных подключена!")
            return conn
        except OperationalError as e:
            if "the database system is starting up" in str(e):
                print("⏳ База данных стартует, ждём...")
                time.sleep(3)
            else:
                print(f"❌ Ошибка БД: {e}")
                raise