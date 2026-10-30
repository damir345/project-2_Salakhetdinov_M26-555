from typing import Dict, List, Tuple

from prettytable import PrettyTable

from .constants import VALID_TYPES
from .decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from .utils import load_table_data

# Кэш для select: ключ — хэш содержимого данных + where_clause
_select_cache = create_cacher()


# ---------- Валидация ----------


def _validate_columns(columns: List[str]) -> None:
    """Проверяет схему столбцов; бросает ValueError при ошибке."""
    for col in columns:
        if ":" not in col:
            raise ValueError(f"Некорректное значение: {col}. Ожидается column:type")
        _, col_type = col.split(":", 1)
        if col_type not in VALID_TYPES:
            raise ValueError(
                f"Некорректное значение: {col_type}. Доступно: int, str, bool"
            )


def _validate_values(columns_schema: list[dict], values: list) -> None:
    """Бросает ValueError, если значения не соответствуют схеме (без ID)."""
    expected = [c for c in columns_schema if c["name"] != "ID"]
    if len(values) != len(expected):
        raise ValueError(
            f"Некорректное значение: ожидалось {len(expected)} значений, "
            f"получено {len(values)}."
        )
    for col, val in zip(expected, values):
        if col["type"] == "bool" and not isinstance(val, bool):
            raise ValueError(f"Некорректное значение: {val} не bool для {col['name']}.")
        if col["type"] == "int" and (not isinstance(val, int) or isinstance(val, bool)):
            raise ValueError(f"Некорректное значение: {val} не int для {col['name']}.")
        if col["type"] == "str" and not isinstance(val, str):
            raise ValueError(f"Некорректное значение: {val} не str для {col['name']}.")


# ---------- Управление таблицами ----------


@handle_db_errors
def create_table(
    metadata: Dict, table_name: str, columns: List[str]
) -> Tuple[Dict, bool]:
    """Создаёт таблицу с автоматическим ID:int; возвращает (metadata, ok)."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata, False

    _validate_columns(columns)

    full_columns = ["ID:int"] + columns
    metadata[table_name] = {
        "columns": [
            {"name": n, "type": t} for n, t in (c.split(":", 1) for c in full_columns)
        ]
    }
    columns_str = ", ".join(full_columns)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_str}')
    return metadata, True


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata: Dict, table_name: str) -> Tuple[Dict, bool]:
    """Удаляет таблицу; возвращает (metadata, ok)."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata, False
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata, True


def list_tables(metadata: Dict) -> None:
    """Печатает список таблиц."""
    if not metadata:
        print("Таблиц нет.")
        return
    for name in metadata:
        print(f"- {name}")


# ---------- CRUD ----------


@handle_db_errors
@log_time
def insert(metadata: dict, table_name: str, values: list) -> Tuple[list, bool]:
    """Добавляет запись с автоинкрементным ID; возвращает (data, ok)."""
    if table_name not in metadata:
        raise KeyError(f'"{table_name}"')

    schema = metadata[table_name]["columns"]
    _validate_values(schema, values)

    data = load_table_data(table_name)
    new_id = max((row["ID"] for row in data), default=0) + 1

    row = {"ID": new_id}
    non_id_cols = [c for c in schema if c["name"] != "ID"]
    for col, val in zip(non_id_cols, values):
        row[col["name"]] = val

    data.append(row)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return data, True


def _make_select_key(table_data: list, where_clause: dict | None) -> tuple:
    """Хэшируемый ключ для кэша: содержимое данных + where_clause."""
    rows_key = tuple(tuple(sorted(row.items())) for row in table_data)
    where_key = tuple(sorted((where_clause or {}).items()))
    return rows_key, where_key


def _do_select(table_data: list, where_clause: dict | None) -> list:
    """Фильтрует записи по where_clause (без кэша)."""
    if where_clause is None:
        return table_data
    return [
        row
        for row in table_data
        if all(row.get(k) == v for k, v in where_clause.items())
    ]


@handle_db_errors
@log_time
def select(table_data: list, where_clause: dict | None = None) -> list:
    """Возвращает записи по условию; результат кэшируется."""
    key = _make_select_key(table_data, where_clause)
    return _select_cache(key, lambda: _do_select(table_data, where_clause))


@handle_db_errors
def update(
    table_name: str,
    table_data: list,
    set_clause: dict,
    where_clause: dict,
) -> Tuple[list, bool]:
    """Обновляет записи по where_clause; возвращает (data, ok)."""
    updated_ids = []
    for row in table_data:
        if all(row.get(k) == v for k, v in where_clause.items()):
            row.update(set_clause)
            updated_ids.append(row["ID"])

    if not updated_ids:
        print("Ошибка: записей, подходящих под условие, не найдено.")
        return table_data, False

    for rid in updated_ids:
        print(f'Запись с ID={rid} в таблице "{table_name}" успешно обновлена.')
    return table_data, True


@handle_db_errors
@confirm_action("удаление записей")
def delete(
    table_name: str,
    table_data: list,
    where_clause: dict,
) -> Tuple[list, bool]:
    """Удаляет записи по where_clause; возвращает (data, ok)."""
    remaining, deleted_ids = [], []
    for row in table_data:
        if all(row.get(k) == v for k, v in where_clause.items()):
            deleted_ids.append(row["ID"])
        else:
            remaining.append(row)

    if not deleted_ids:
        print("Ошибка: записей, подходящих под условие, не найдено.")
        return table_data, False

    for rid in deleted_ids:
        print(f'Запись с ID={rid} успешно удалена из таблицы "{table_name}".')
    return remaining, True


# ---------- Вывод ----------


def print_table(rows: list) -> None:
    """Печатает список словарей через PrettyTable."""
    if not rows:
        print("(нет записей)")
        return
    table = PrettyTable()
    table.field_names = list(rows[0].keys())
    for row in rows:
        table.add_row([row[k] for k in rows[0].keys()])
    print(table)


@handle_db_errors
def info(metadata: dict, table_name: str) -> None:
    """Печатает схему таблицы и количество записей."""
    if table_name not in metadata:
        raise KeyError(f'"{table_name}"')
    schema = metadata[table_name]["columns"]
    cols_str = ", ".join(f"{c['name']}:{c['type']}" for c in schema)
    data = load_table_data(table_name)
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {cols_str}")
    print(f"Количество записей: {len(data)}")
