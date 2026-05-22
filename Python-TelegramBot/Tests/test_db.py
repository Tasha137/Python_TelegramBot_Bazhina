import pytest
from db_utils import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
import psycopg2


@pytest.fixture
def test_db_conn():
    """Соединение с БД тестов."""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )
    yield conn
    conn.close()


def test_create_event(test_db_conn):
    """Проверяет, что событие корректно создаётся в БД."""
    cursor = test_db_conn.cursor()

    cursor.execute(
        """
        INSERT INTO events
            (user_id, name, date, time, description)
        VALUES
            (123, 'Test Event', '2026-04-06',
            '10:00:00', 'Test description')
        RETURNING id;
        """
    )

    event_id = cursor.fetchone()[0]

    cursor.execute(
        "SELECT name,"
        " date,"
        " time FROM events " "WHERE id = %s", (event_id,)
    )
    name, date, time = cursor.fetchone()

    assert name == "Test Event"
    assert str(date) == "2026-04-06"
    assert str(time) == "10:00:00"

    cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
    test_db_conn.commit()
