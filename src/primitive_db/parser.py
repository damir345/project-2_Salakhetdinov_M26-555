import shlex
from typing import Optional


def cast_value(raw: str):
    """Приводит строку к int/bool/str; снимает обрамляющие кавычки."""
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ('"', "'"):
        raw = raw[1:-1]
    lowered = raw.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    try:
        return int(raw)
    except ValueError:
        return raw


def parse_condition(tokens: list[str]) -> Optional[dict]:
    """Разбирает ['col', '=', 'val'] в {'col': val}."""
    if len(tokens) != 3 or tokens[1] != "=":
        return None
    return {tokens[0]: cast_value(tokens[2])}


def parse_set_clause(tokens: list[str]) -> Optional[dict]:
    """Разбирает ['col1', '=', 'v1', ...] в {'col1': v1, ...}."""
    if not tokens or len(tokens) % 3 != 0:
        return None
    result = {}
    for i in range(0, len(tokens), 3):
        col, eq, val = tokens[i], tokens[i + 1], tokens[i + 2]
        if eq != "=":
            return None
        result[col] = cast_value(val)
    return result


def split_values(values_str: str) -> list[str]:
    """Разбирает строку значений из (...) в список строковых токенов.

    'values_str' — содержимое между скобками, например: '"Sergei", 28, true'
    """
    result = []
    for chunk in values_str.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        # shlex.split снимет кавычки и корректно обработает пробелы
        parts = shlex.split(chunk)
        if parts:
            result.append(parts[0])
    return result
