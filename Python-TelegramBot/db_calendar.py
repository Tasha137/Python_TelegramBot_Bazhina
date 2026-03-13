import psycopg2
from psycopg2 import sql
from datetime import datetime
import re


class Calendar:
    def __init__(self, conn_or_config):
        """
        Принимает либо готовое соединение conn ИЛИ конфиг dict
        """
        if isinstance(conn_or_config, dict):
            # Если передали конфиг → подключаемся сами
            self.db_config = conn_or_config
            self.conn = None
            self._connect()
        else:
            # Если передали готовое соединение conn
            self.conn = conn_or_config
            print("✅ Calendar использует переданное соединение conn!")

    def _connect(self):
        """Подключение к базе данных (если передали конфиг)"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            print("✅ Подключение к БД успешно!")
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")

    def _get_cursor(self):
        """Получить курсор с обработкой ошибок"""
        if self.conn is None or self.conn.closed:
            self._connect()
        return self.conn.cursor()

    def create_event(self, event_name, event_date, event_time, event_details=""):
        """📥 Создать событие в таблице events"""
        try:
            cur = self._get_cursor()

            # Вставка новой строки
            cur.execute("""
                INSERT INTO events (name, date, time, details) 
                VALUES (%s, %s, %s, %s)
            """, (event_name, event_date, event_time, event_details))

            self.conn.commit()
            cur.close()
            print(f"✅ Событие '{event_name}' создано!")
            return True

        except Exception as e:
            print(f"❌ Ошибка создания события: {e}")
            self.conn.rollback()
            return False

    def read_event(self, event_name):
        """🔍 Найти событие по имени"""
        try:
            cur = self._get_cursor()

            cur.execute("""
                SELECT id, name, date, time, details 
                FROM events 
                WHERE name ILIKE %s
            """, (f"%{event_name}%",))

            events = cur.fetchall()
            cur.close()

            if events:
                print(f"\n📋 Найдено событие '{event_name}':")
                for event in events:
                    print(
                        f"  ID: {event[0]}, Название: {event[1]}, Дата: {event[2]}, Время: {event[3]}, Детали: {event[4]}")
                return events
            else:
                print(f"❌ Событие '{event_name}' не найдено")
                return []

        except Exception as e:
            print(f"❌ Ошибка поиска: {e}")
            return []

    def display_events(self):
        """📊 Показать все события"""
        try:
            cur = self._get_cursor()

            cur.execute("""
                SELECT id, name, date, time, details 
                FROM events 
                ORDER BY date, time
            """)

            events = cur.fetchall()
            cur.close()

            if events:
                print("\n📅 ВСЕ СОБЫТИЯ:")
                print("-" * 60)
                for event in events:
                    print(f"ID: {event[0]:2} | {event[1]:20} | {event[2]} {event[3]:8} | {event[4]}")
                print("-" * 60)
            else:
                print("📭 Календарь пуст")

            return events

        except Exception as e:
            print(f"❌ Ошибка отображения: {e}")
            return []

    def edit_event(self, event_name, new_date=None, new_description=None):
        """✏️ Изменить событие"""
        try:
            cur = self._get_cursor()

            # Обновление полей
            if new_date and new_description:
                cur.execute("""
                    UPDATE events 
                    SET date = %s, details = %s 
                    WHERE name ILIKE %s
                """, (new_date, new_description, f"%{event_name}%"))
            elif new_date:
                cur.execute("""
                    UPDATE events SET date = %s WHERE name ILIKE %s
                """, (new_date, f"%{event_name}%"))
            elif new_description:
                cur.execute("""
                    UPDATE events SET details = %s WHERE name ILIKE %s
                """, (new_description, f"%{event_name}%"))

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

            cur.execute("""
                DELETE FROM events WHERE name ILIKE %s
            """, (f"%{event_name}%",))

            rows_deleted = cur.rowcount
            self.conn.commit()
            cur.close()

            if rows_deleted > 0:
                print(f"✅ Удалено {rows_deleted} событие(ий)")
                return True
            else:
                print(f"❌ Событие '{event_name}' не найдено")
                return False

        except Exception as e:
            print(f"❌ Ошибка удаления: {e}")
            self.conn.rollback()
            return False

    def __del__(self):
        """Закрытие соединения"""
        if self.conn and not self.conn.closed:
            self.conn.close()
            print("🔌 БД отключена")
