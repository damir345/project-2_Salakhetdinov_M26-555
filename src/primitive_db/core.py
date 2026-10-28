from typing import Dict, List, Tuple

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
            {"name": n, "type": t}
            for n, t in (c.split(":", 1) for c in full_columns)
        ]
    }
    print(
        f'Таблица "{table_name}" успешно создана '
        f'со столбцами: {", ".join(full_columns)}'
    )
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