from notes_service import (
    create_note,
    read_note,
    edit_note,
    delete_note,
    display_notes,
    display_sorted_notes,
)


def handle_create():
    name = input("Название: ")
    text = input("Текст: ")
    success, msg = create_note(name, text)
    print(msg)


def handle_read():
    name = input("Название: ")
    success, content = read_note(name)
    print(content)


def handle_edit():
    name = input("Название: ")
    new_text = input("Новый текст: ")
    success, msg = edit_note(name, new_text)
    print(msg)


def handle_delete():
    name = input("Название: ")
    success, msg = delete_note(name)
    print(msg)


def handle_display(reverse=False):
    if reverse:
        success, notes = display_sorted_notes()
        print("Заметки (короткие→длинные):")
    else:
        success, notes = display_notes()
        print("Заметки (длинные→короткие):")

    if success and notes:
        for note in notes:
            print(f"- {note[:-4]}")  # без расширения .txt
    else:
        print("Заметок нет")


def show_menu():
    return input(
        "1 - создать\n"
        "2 - прочитать\n"
        "3 - редактировать\n"
        "4 - удалить\n"
        "5 - все заметки (длинные→короткие)\n"
        "6 - все заметки (короткие→длинные)\n"
        "n - выход\n"
        ">>> "
    ).lower()


def main():
    while True:
        action = show_menu()

        if action == "1":
            handle_create()
        elif action == "2":
            handle_read()
        elif action == "3":
            handle_edit()
        elif action == "4":
            handle_delete()
        elif action == "5":
            handle_display(reverse=False)
        elif action == "6":
            handle_display(reverse=True)
        elif action == "n":
            break
        else:
            print("Введите 1–6 или n")

        if action != "n":
            input("\nEnter для продолжения...")


if __name__ == "__main__":
    main()
