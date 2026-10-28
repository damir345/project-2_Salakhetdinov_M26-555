import shlex
import sys

from . import core
from .utils import load_metadata, save_metadata

DB_FILE = "db_meta.json"


def print_help() -> None:
    """Печатает справку по командам."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def _print_welcome() -> None:
    print("***База данных***")
    print_help()


def run() -> None:
    """Главный цикл программы."""
    _print_welcome()

    while True:
        try:
            user_input = input(">>>Введите команду: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nВыход.")
            sys.exit(0)

        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError as e:
            print(f"Некорректное значение: {user_input}. Попробуйте снова. ({e})")
            continue

        command, *params = args
        metadata = load_metadata(DB_FILE)

        if command == "create_table":
            if len(params) < 2:
                print("Некорректное значение: недост. аргументов для create_table.")
                continue
            metadata, ok = core.create_table(metadata, params[0], params[1:])
            if ok:
                save_metadata(DB_FILE, metadata)

        elif command == "drop_table":
            if len(params) != 1:
                print("Некорректное значение: drop_table требует "
                       "ровно одно имя таблицы.")
                continue
            metadata, ok = core.drop_table(metadata, params[0])
            if ok:
                save_metadata(DB_FILE, metadata)

        elif command == "list_tables":
            if params:
                print("Некорректное значение: list_tables не принимает аргументов.")
                continue
            core.list_tables(metadata)

        elif command == "help":
            print_help()

        elif command == "exit":
            print("Выход из программы.")
            break

        else:
            print(f"Функции {command} нет. Попробуйте снова.")