import psycopg2
from datetime import datetime


class Calendar:
    def __init__(self, conn):
        self.conn = conn

    def _get_cursor(self):
        return self.conn.cursor()

    def register_user(self, user_id, username=None, first_name=None):
        try:
            cur = self._get_cursor()
            cur.execute("""
                INSERT INTO users (user_id, username, first_name) 
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id) DO NOTHING
            """, (user_id, username, first_name))
            self.conn.commit()
            cur.close()
            print(f"✅ Пользователь {user_id} зарегистрирован")
            return True
        except Exception as e:
            print(f"❌ РЕГИСТРАЦИЯ ОШИБКА: {e}")
            self.conn.rollback()
            return False

    def create_event(self, user_id, name, date_str, time_str, description):
        print(f"🔍 DEBUG user_id: {user_id}")
        try:
            cur = self._get_cursor()
            # ✅ ЯВНО указываем id = DEFAULT и user_id ПЕРВЫМ!
            cur.execute("""
                INSERT INTO events (id, user_id, name, date, time, description) 
                VALUES (DEFAULT, %s, %s, %s, %s, %s)
            """, (user_id, name, date_str, time_str, description))
            self.conn.commit()
            cur.close()
            print(f"✅ СОЗДАНО: {name} для user_id {user_id}")
            return True
        except Exception as e:
            print(f"❌ ОШИБКА: {e}")
            self.conn.rollback()
            return False

    def get_user_events(self, user_id):
        try:
            cur = self._get_cursor()
            cur.execute("""
                SELECT id, name, date, time, description 
                FROM events 
                WHERE user_id = %s 
                ORDER BY date, time
            """, (user_id,))

            columns = ['id', 'name', 'date', 'time', 'description']
            events = []
            for row in cur.fetchall():
                events.append(dict(zip(columns, row)))

            cur.close()
            print(f"✅ Найдено событий для {user_id}: {len(events)}")
            return events
        except Exception as e:
            print(f"❌ GET_EVENTS: {e}")
            return []

    def delete_event(self, user_id, event_id):
        try:
            cur = self._get_cursor()
            cur.execute("""
                DELETE FROM events 
                WHERE id = %s AND user_id = %s
            """, (event_id, user_id))
            deleted = cur.rowcount
            self.conn.commit()
            cur.close()
            return deleted > 0
        except Exception as e:
            print(f"❌ DELETE ОШИБКА: {e}")
            self.conn.rollback()
            return False
