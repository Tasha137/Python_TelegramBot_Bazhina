import os

# Создайте функцию, которая создает заметку по запросу пользователя
def build_note(note_text: str, note_name: str) -> tuple[bool, str]:
    """
    Создаёт/перезаписывает файл с заметкой.
    Возвращает (успех: bool, сообщение: str), чтобы бот сам решил, что показать пользователю.
    """
    try:
        try:
            # Пытаемся открыть существующий файл для чтения/записи
            file = open(f"{note_name}.txt", "r+", encoding="utf-8")
            file_exists = True
        except IOError:
            # Если файла нет — создаём новый
            file = open(f"{note_name}.txt", "w+", encoding="utf-8")
            file_exists = False

        file.write(note_text)
        file.close()

        if file_exists:
            msg = f"Заметка '{note_name}' обновлена."
        else:
            msg = f"Заметка '{note_name}' создана."

        return True, msg

    except Exception as e:
        # Можно вернуть текст ошибки, чтобы логировать или отправить пользователю
        return False, "Не удалось сохранить заметку. Попробуйте ещё раз."


# Напишите функцию, которая запрашивает название и текст заметки, а затем создает ее
def create_note(note_name: str, note_text: str) -> tuple[bool, str]:
    """
    Создаёт заметку с проверкой названия на запрещённые символы.
    Возвращает (успех: bool, сообщение: str)
    """
    # Проверка на запрещённые символы Windows
    forbidden_symbols = "\\|/*<>?:"
    if any(symbol in note_name for symbol in forbidden_symbols):
        return False, "Название содержит недопустимые символы (\\|/*<>?:). Переименуйте заметку."

    # Вызываем функцию сохранения
    success, message = build_note(note_text, note_name)

    if success:
        return True, f"✅ Заметка '{note_name}' создана."
    else:
        return False, message


# Напишите функцию, которая прочитает заметку и выведет ее текст
def read_note(note_name: str) -> tuple[bool, str]:
    """
    Читает заметку из файла и возвращает её текст.
    Возвращает (успех: bool, содержимое: str)
    """
    try:
        path = f"{note_name}.txt"

        # Проверяем существование файла
        if not os.path.isfile(path):
            return False, "❌ Такой заметки не существует."

        # Читаем файл
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()

        return True, content.strip()

    except Exception:
        return False, "❌ Не удалось прочитать заметку. Попробуйте ещё раз."


# Напишите функцию, которая удаляет заметку
def delete_note(note_name: str) -> tuple[bool, str]:
    """
    Удаляет заметку из файла.
    Возвращает (успех: bool, сообщение: str)
    """
    try:
        path = f"{note_name}.txt"

        # Проверяем существование файла
        if not os.path.isfile(path):
            return False, "❌ Такой заметки не существует."

        # Удаляем файл
        os.remove(path)
        return True, f"✅ Заметка '{note_name}' удалена."

    except Exception:
        return False, "❌ Не удалось удалить заметку. Попробуйте ещё раз."


# Напишите функцию редактирования заметки
def edit_note(note_name: str, new_text: str) -> tuple[bool, str]:
    """
    Редактирует существующую заметку.
    Возвращает (успех: bool, сообщение: str)
    """
    try:
        path = f"{note_name}.txt"

        # Проверяем существование файла
        if not os.path.isfile(path):
            return False, "❌ Такой заметки не существует."

        # Перезаписываем файл
        with open(path, "w", encoding="utf-8") as file:
            file.write(new_text)

        return True, f"✅ Заметка '{note_name}' обновлена."

    except Exception:
        return False, "❌ Не удалось отредактировать заметку. Попробуйте ещё раз."


# Напишите функцию, которая выведет все заметки пользователя в порядке от самой короткой до самой длинной
def display_notes() -> tuple[bool, list[str]]:
    """
    Возвращает список всех заметок, отсортированных по длине имени (от длинных к коротким).
    Возвращает (успех: bool, список_заметок: list[str])
    """
    try:
        # Получаем все .txt файлы
        notes = [note for note in os.listdir('.') if note.endswith(".txt")]

        # Сортируем по длине имени (от длинных к коротким)
        sorted_notes = sorted(notes, key=len, reverse=True)

        return True, sorted_notes

    except Exception:
        return False, []


# Напишите функцию, которая выведет все заметки пользователя в порядке от самой длинной до самой короткой
def display_sorted_notes() -> tuple[bool, list[str]]:
    """
    Возвращает список всех заметок, отсортированных по длине имени (от коротких к длинным).
    Возвращает (успех: bool, список_заметок: list[str])
    """
    try:
        # Получаем все .txt файлы
        notes = [note for note in os.listdir('.') if note.endswith(".txt")]

        # Сортируем по длине имени (от коротких к длинным)
        sorted_notes = sorted(notes, key=len)

        return True, sorted_notes

    except Exception:
        return False, []


class Calendar:
    def __init__(self):
        self.events = {}

    def create_event(self, event_name, event_date, event_time, event_details):
        event_id = len(self.events) + 1
        event = {
            "id": event_id,
            "name": event_name,
            "date": event_date,
            "time": event_time,
            "details": event_details
        }
        self.events[event_id] = event
        return True, f"✅ Событие '{event_name}' создано (ID: {event_id})"

    def read_event(self, event_id):
        event = self.events.get(int(event_id))
        if event:
            return True, f"📅 *{event['name']}*\n🗓️ {event['date']} {event['time']}\n📝 {event['details']}"
        return False, "❌ Событие не найдено"

    def list_events(self):
        if self.events:
            text = "📅 *Все события:*\n\n"
            for event_id, event in self.events.items():
                text += f"ID {event_id}: *{event['name']}* ({event['date']} {event['time']})\n"
            return True, text
        return True, "📭 Событий нет"

calendar = Calendar()