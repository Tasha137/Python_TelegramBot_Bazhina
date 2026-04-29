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

    def create_event(self, event_name, event_date, event_time):
        """📥 Создать событие в таблице events"""
        try:
            cur = self._get_cursor()

            cur.execute(
                """
                INSERT INTO events (user_id, name, date, time)
                VALUES (1, %s, %s, %s)
            """,
                (event_name, event_date, event_time),
            )

            self.conn.commit()
            cur.close()
            print(f"✅ Пользователь {user_id} зарегистрирован")
            return True
        except Exception as e:

            print(f"❌ РЕГИСТРАЦИЯ ОШИБКА: {e}")
            self.conn.rollback()

            print(f"❌ Ошибка создания события: {e}")

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

            cur.execute(
                """
                SELECT id, name, date, time, details
                FROM events
                WHERE name ILIKE %s
            """,
                (f"%{event_name}%",),
            )

            events = cur.fetchall()
            cur.close()

            if events:
                print(f"\n📋 Найдено событие '{event_name}':")
                for event in events:
                    print(
                        f"  ID: {event[0]}, "
                        f"Название: {event[1]}, "
                        f"Дата: {event[2]}, Время: {event[3]}, "
                        f"Детали: {event[4]}"
                    )
                return events
            else:
                print(f"❌ Событие '{event_name}' не найдено")
                return []

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

            cur.execute(
                """
                SELECT id, name, date, time, details
                FROM events
                ORDER BY date, time
            """
            )

            cur.close()

            print(f"✅ Найдено событий для {user_id}: {len(events)}")

            if events:
                print("\n📅 ВСЕ СОБЫТИЯ:")
                print("-" * 60)
                for event in events:
                    print(
                        f"ID: {event[0]:2} | {event[1]:20} | "
                        f"{event[2]} {event[3]:8} | {event[4]}"
                    )
                print("-" * 60)
            else:
                print("📭 Календарь пуст")

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

            # Обновление полей
            if new_date and new_description:
                cur.execute(
                    """
                    UPDATE events
                    SET date = %s, details = %s
                    WHERE name ILIKE %s
                """,
                    (new_date, new_description, f"%{event_name}%"),
                )
            elif new_date:
                cur.execute(
                    """
                    UPDATE events SET date = %s WHERE name ILIKE %s
                """,
                    (new_date, f"%{event_name}%"),
                )
            elif new_description:
                cur.execute(
                    """
                    UPDATE events SET details = %s WHERE name ILIKE %s
                """,
                    (new_description, f"%{event_name}%"),
                )

            rows_updated = cur.rowcount
            self.conn.commit()
            cur.close()

            if rows_updated > 0:
                print(f"✅ Обновлено {rows_updated} событие(ий)")
                return True
            else:
                print(f"❌ Событие '{event_name}' не найдено")
                return False

        except Exception as e:
            print(f"❌ Ошибка редактирования: {e}")
            self.conn.rollback()
            return False

    def delete_event(self, event_name):
        """🗑️ Удалить событие"""
        try:
            cur = self._get_cursor()

            cur.execute(
                """
                DELETE FROM events WHERE name ILIKE %s
            """,
                (f"%{event_name}%",),
            )

            rows_deleted = cur.rowcount
            self.conn.commit()
            cur.close()
            return deleted > 0
        except Exception as e:
            print(f"❌ DELETE ОШИБКА: {e}")
            self.conn.rollback()
            return False
