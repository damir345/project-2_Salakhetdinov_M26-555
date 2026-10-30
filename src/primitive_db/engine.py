import shlex
import sys

from . import core, parser
from .utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

DB_FILE = "db_meta.json"

MIN_CREATE_ARGS = 3
MIN_SELECT_ARGS = 3
MIN_UPDATE_ARGS = 3
MIN_DELETE_ARGS = 4
EXACT_ONE_ARG = 2


def print_help() -> None:
    print("\n***Операции с данными***")
    print("Функции:")
    print(
        "<command> insert into <имя_таблицы> values "
        "(<значение1>, <значение2>, ...) - создать запись"
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = "
        "<значение> - прочитать записи по условию"
    )
    print("<command> select from <имя_таблицы> - прочитать все записи")
    print(
        "<command> update <имя_таблицы> set <столбец1> = <значение1> "
        "where <столбец> = <значение> - обновить запись"
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = "
        "<значение> - удалить запись"
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def parse_insert(user_input: str):
    tokens = user_input.split()
    if len(tokens) < 5:
        return None
    if tokens[0].lower() != "insert" or tokens[1].lower() != "into":
        return None
    if tokens[3].lower() != "values":
        return None
    table_name = tokens[2]

    rest = user_input.split("values", 1)[1].strip()
    if not (rest.startswith("(") and rest.endswith(")")):
        return None
    values_str = rest[1:-1]
    return table_name, values_str


def split_by_token(tokens: list[str], keyword: str):
    if keyword in tokens:
        idx = tokens.index(keyword)
        return tokens[:idx], tokens[idx + 1 :]
    return tokens, []


def handle_create_table(user_input: str) -> None:
    parts = user_input.split()
    if len(parts) < MIN_CREATE_ARGS:
        print("Некорректное значение: недостаточно аргументов.")
        return
    metadata = load_metadata(DB_FILE)
    result = core.create_table(metadata, parts[1], parts[2:])
    if result is None:
        return
    metadata, ok = result
    if ok:
        save_metadata(DB_FILE, metadata)


def handle_drop_table(user_input: str) -> None:
    parts = user_input.split()
    if len(parts) != EXACT_ONE_ARG:
        print("Некорректное значение: drop_table требует одно имя.")
        return
    metadata = load_metadata(DB_FILE)
    result = core.drop_table(metadata, parts[1])
    if result is None:
        # отменено пользователем или перехвачена ошибка
        return
    metadata, ok = result
    if ok:
        save_metadata(DB_FILE, metadata)
        delete_table_data(parts[1])


def handle_list_tables(_: str) -> None:
    core.list_tables(load_metadata(DB_FILE))


def handle_info(user_input: str) -> None:
    parts = user_input.split()
    if len(parts) != EXACT_ONE_ARG:
        print("Некорректное значение: info требует одно имя таблицы.")
        return
    core.info(load_metadata(DB_FILE), parts[1])


def handle_insert(user_input: str) -> None:
    parsed = parse_insert(user_input)
    if not parsed:
        print("Некорректное значение: неверный синтаксис insert.")
        return
    table_name, values_str = parsed
    raw_values = parser.split_values(values_str)
    values = [parser.cast_value(v) for v in raw_values]
    metadata = load_metadata(DB_FILE)
    result = core.insert(metadata, table_name, values)
    if result is None:
        return
    data, ok = result
    if ok:
        save_table_data(table_name, data)


def handle_select(user_input: str) -> None:
    tokens = shlex.split(user_input)
    if len(tokens) < MIN_SELECT_ARGS or tokens[1] != "from":
        print("Некорректное значение: неверный синтаксис select.")
        return
    table_name = tokens[2]
    _, where_tokens = split_by_token(tokens[3:], "where")
    where_clause = None
    if where_tokens:
        where_clause = parser.parse_condition(where_tokens)
        if where_clause is None:
            print("Некорректное значение: неверное условие where.")
            return
    if table_name not in load_metadata(DB_FILE):
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return
    data = load_table_data(table_name)
    rows = core.select(data, where_clause)
    if rows is None:
        return
    core.print_table(rows)


def handle_update(user_input: str) -> None:
    tokens = shlex.split(user_input)
    if len(tokens) < MIN_UPDATE_ARGS:
        print("Некорректное значение: неверный синтаксис update.")
        return
    table_name = tokens[1]
    rest, where_tokens = split_by_token(tokens[2:], "where")
    if not where_tokens or "set" not in rest:
        print("Некорректное значение: update требует set ... where ...")
        return
    set_idx = rest.index("set")
    set_clause = parser.parse_set_clause(rest[set_idx + 1 :])
    where_clause = parser.parse_condition(where_tokens)
    if set_clause is None or where_clause is None:
        print("Некорректное значение: неверный set или where.")
        return
    if table_name not in load_metadata(DB_FILE):
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return
    data = load_table_data(table_name)
    result = core.update(table_name, data, set_clause, where_clause)
    if result is None:
        return
    data, ok = result
    if ok:
        save_table_data(table_name, data)


def handle_delete(user_input: str) -> None:
    tokens = shlex.split(user_input)
    if len(tokens) < MIN_DELETE_ARGS or tokens[1] != "from":
        print("Некорректное значение: неверный синтаксис delete.")
        return
    table_name = tokens[2]
    _, where_tokens = split_by_token(tokens[3:], "where")
    where_clause = parser.parse_condition(where_tokens) if where_tokens else None
    if where_clause is None:
        print("Некорректное значение: delete требует where col = val.")
        return
    if table_name not in load_metadata(DB_FILE):
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return
    data = load_table_data(table_name)
    result = core.delete(table_name, data, where_clause)
    if result is None:
        return
    data, ok = result
    if ok:
        save_table_data(table_name, data)


HANDLERS = {
    "create_table": handle_create_table,
    "drop_table": handle_drop_table,
    "list_tables": handle_list_tables,
    "info": handle_info,
    "insert": handle_insert,
    "select": handle_select,
    "update": handle_update,
    "delete": handle_delete,
}


def dispatch(user_input: str) -> bool:
    """Возвращает True, если нужно выйти из цикла."""
    lower = user_input.lower()

    if lower == "help":
        print_help()
        return False
    if lower == "exit":
        print("Выход из программы.")
        return True

    first_word = lower.split()[0]
    handler = HANDLERS.get(first_word)
    if handler is None:
        print(f"Функции {first_word} нет. Попробуйте снова.")
        return False

    handler(user_input)
    return False


def run() -> None:
    print("***База данных***")
    print_help()

    while True:
        try:
            user_input = input(">>>Введите команду: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nВыход.")
            sys.exit(0)

        if not user_input:
            continue

        if dispatch(user_input):
            break
