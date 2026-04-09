class Calendar:
    def __init__(self, conn):
        self.conn = conn
        self.events = []

    def add_event(self, name, start_time, end_time, user_id):
        """Добавляет событие в БД."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO events (name, start_time, end_time, user_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (name, start_time, end_time, user_id),
        )
        event_id = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return event_id

    def get_events(self):
        """Возвращает все события."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id,"
            " name,"
            " start_time,"
            " end_time,"
            " user_id FROM events"
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def delete_event(self, event_id):
        """Удаляет событие по ID."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
        self.conn.commit()
        cursor.close()

    def edit_event(self, event_id, name, start_time, end_time, user_id):
        """Редактирует событие."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE events
            SET name = %s, start_time = %s, end_time = %s, user_id = %s
            WHERE id = %s
            """,
            (name, start_time, end_time, user_id, event_id),
        )
        self.conn.commit()
        cursor.close()
