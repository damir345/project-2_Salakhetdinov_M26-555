from typing import Dict, List, Tuple

from prettytable import PrettyTable

from .utils import load_table_data

ALLOWED_TYPES = {"int", "str", "bool"}


def _validate_columns(columns: List[str]) -> Tuple[bool, str]:
    for col in columns:
        if ":" not in col:
            return False, f"Некорректное значение: {col}. Ожидается column:type"
        _, col_type = col.split(":", 1)
        if col_type not in ALLOWED_TYPES:
            return False, f"Некорректное значение: {col_type}. Доступно: int, str, bool"
    return True, ""


def create_table(
    metadata: Dict, table_name: str, columns: List[str]
) -> Tuple[Dict, bool]:
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata, False

    ok, err = _validate_columns(columns)
    if not ok:
        print(err)
        return metadata, False

    full_columns = ["ID:int"] + columns
    metadata[table_name] = {
        "columns": [
            {"name": n, "type": t} for n, t in (c.split(":", 1) for c in full_columns)
        ]
    }
    columns_str = ", ".join(full_columns)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_str}')
    return metadata, True


def drop_table(metadata: Dict, table_name: str) -> Tuple[Dict, bool]:
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata, False
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata, True


def list_tables(metadata: Dict) -> None:
    if not metadata:
        print("Таблиц нет.")
        return
    for name in metadata:
        print(f"- {name}")


def _validate_values(columns_schema: list[dict], values: list) -> tuple[bool, str]:
    expected = [c for c in columns_schema if c["name"] != "ID"]
    if len(values) != len(expected):
        return (
            False,
            f"Некорректное значение: ожидалось {len(expected)} значений, "
            f"получено {len(values)}.",
        )
    for col, val in zip(expected, values):
        if col["type"] == "bool":
            if not isinstance(val, bool):
                return False, f"Некорректное значение: {val} не bool для {col['name']}."
        elif col["type"] == "int":
            if not isinstance(val, int) or isinstance(val, bool):
                return False, f"Некорректное значение: {val} не int для {col['name']}."
        elif col["type"] == "str":
            if not isinstance(val, str):
                return False, f"Некорректное значение: {val} не str для {col['name']}."
    return True, ""


def insert(metadata: dict, table_name: str, values: list) -> Tuple[list, bool]:
    """Вставляет запись. values — уже приведённые типы, без ID."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return [], False

    schema = metadata[table_name]["columns"]
    ok, err = _validate_values(schema, values)
    if not ok:
        print(err)
        return [], False

    data = load_table_data(table_name)
    new_id = max((row["ID"] for row in data), default=0) + 1

    row = {"ID": new_id}
    non_id_cols = [c for c in schema if c["name"] != "ID"]
    for col, val in zip(non_id_cols, values):
        row[col["name"]] = val

    data.append(row)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return data, True


def select(table_data: list, where_clause: dict | None = None) -> list:
    if where_clause is None:
        return table_data
    return [
        row
        for row in table_data
        if all(row.get(k) == v for k, v in where_clause.items())
    ]


def update(
    table_name: str,
    table_data: list,
    set_clause: dict,
    where_clause: dict,
) -> Tuple[list, bool]:
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


def delete(
    table_name: str,
    table_data: list,
    where_clause: dict,
) -> Tuple[list, bool]:
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


def print_table(rows: list) -> None:
    if not rows:
        print("(нет записей)")
        return
    table = PrettyTable()
    table.field_names = list(rows[0].keys())
    for row in rows:
        table.add_row([row[k] for k in rows[0].keys()])
    print(table)


def info(metadata: dict, table_name: str) -> None:
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return
    schema = metadata[table_name]["columns"]
    cols_str = ", ".join(f"{c['name']}:{c['type']}" for c in schema)
    data = load_table_data(table_name)
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {cols_str}")
    print(f"Количество записей: {len(data)}")
