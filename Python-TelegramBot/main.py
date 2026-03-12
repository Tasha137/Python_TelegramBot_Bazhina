import re
from notes_service import create_note, read_note, edit_note, delete_note, display_notes, display_sorted_notes


def main():
    while True:
        action = input(
            "1 - создать\n2 - прочитать\n3 - редактировать\n4 - удалить\n"
            "5 - все заметки (длинные→короткие)\n6 - все заметки (короткие→длинные)\n"
            "n - выход\n>>> "
        ).lower()

        if re.search(r"[123456n]", action):
            if action == "1":
                name = input("Название: ")
                text = input("Текст: ")
                success, msg = create_note(name, text)
                print(msg)

            elif action == "2":
                name = input("Название: ")
                success, content = read_note(name)
                print(content)

            elif action == "3":
                name = input("Название: ")
                new_text = input("Новый текст: ")
                success, msg = edit_note(name, new_text)
                print(msg)

            elif action == "4":
                name = input("Название: ")
                success, msg = delete_note(name)
                print(msg)

            elif action == "5":
                success, notes = display_notes()
                if success and notes:
                    print("Заметки (длинные→короткие):")
                    for note in notes:
                        print(f"- {note[:-4]}")
                else:
                    print("Заметок нет")

            elif action == "6":
                success, notes = display_sorted_notes()
                if success and notes:
                    print("Заметки (короткие→длинные):")
                    for note in notes:
                        print(f"- {note[:-4]}")
                else:
                    print("Заметок нет")

            elif action == "n":
                break

        else:
            print("Введите 1-6 или n")

        if action != "n":
            input("\nEnter для продолжения...")


if __name__ == "__main__":
    main()

