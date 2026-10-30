# project-2_Salakhetdinov_M26-555

Учебная примитивная база данных на Python: управление таблицами, CRUD-операции,
хранение данных в JSON, вывод через PrettyTable, декораторы для обработки ошибок,
подтверждения опасных операций, замера времени и кэширования.

## Установка

```bash
uv sync
```

## Запуск

```bash
make run
```

Альтернатива без `make`:

```bash
uv run database
```

## Структура проекта

```
src/primitive_db/
├── main.py          # точка входа
├── engine.py        # главный цикл, парсинг команд, вызовы core
├── core.py          # бизнес-логика: таблицы и CRUD
├── utils.py         # чтение/запись JSON (метаданные и данные таблиц)
├── parser.py        # разбор where / set / values
├── decorators.py    # handle_db_errors, confirm_action, log_time, create_cacher
└── constants.py     # META_FILE, DATA_DIR, VALID_TYPES, MIN_*_ARGS
```

## Линтер

```bash
make lint
```

Альтернатива:

```bash
uv run ruff check .
uv run ruff format --check .
```

## Управление таблицами

После установки запустите:

```bash
uv run database
```

## CRUD-операции

После создания таблицы можно работать с данными внутри неё.

| Команда | Описание |
|---|---|
| `insert into <таблица> values (<v1>, <v2>, ...)` | Добавить запись. `ID` генерируется автоматически и **не** передаётся. |
| `select from <таблица>` | Показать все записи (PrettyTable). |
| `select from <таблица> where <col> = <val>` | Показать записи по условию. |
| `update <таблица> set <col> = <val> where <col> = <val>` | Обновить записи по условию. Поддерживается несколько полей через запятую: `set age = 30, is_active = false`. |
| `delete from <таблица> where <col> = <val>` | Удалить записи по условию. |
| `info <таблица>` | Показать схему таблицы и количество записей. |

### Правила ввода значений

- Строковые значения — **в кавычках**: `"Sergei"`, `"Anna"`.
- Логические — `true` / `false` без кавычек (регистр не важен: `True`, `TRUE` тоже работают).
- Числовые — без кавычек: `28`, `500`.
- Логические значения в `where` работают так же: `where is_active = true`.

### Хранение

- Метаданные всех таблиц: `db_meta.json`.
- Данные каждой таблицы: `data/<имя_таблицы>.json`.
- При `drop_table` удаляются и метаданные, и файл данных.

### Пример

```
>>>Введите команду: create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool

>>>Введите команду: insert into users values ("Sergei", 28, true)
Запись с ID=1 успешно добавлена в таблицу "users".

>>>Введите команду: select from users where age = 28
+----+--------+-----+-----------+
| ID |  name  | age | is_active |
+----+--------+-----+-----------+
| 1  | Sergei | 28  |    True   |
+----+--------+-----+-----------+

>>>Введите команду: update users set age = 29 where name = "Sergei"
Запись с ID=1 в таблице "users" успешно обновлена.

>>>Введите команду: delete from users where ID = 1
Запись с ID=1 успешно удалена из таблицы "users".

>>>Введите команду: info users
Таблица: users
Столбцы: ID:int, name:str, age:int, is_active:bool
Количество записей: 0
```

## Обработка ошибок, подтверждения и кэширование

В проекте реализованы декораторы (`src/primitive_db/decorators.py`):

### `handle_db_errors`

Централизованно перехватывает типичные ошибки БД:
- `KeyError` – «Ошибка: Таблица или столбец ... не найден.»
- `ValueError` – «Ошибка валидации: ...»
- `FileNotFoundError` – «Ошибка: Файл данных не найден. ...»
- любое другое исключение – «Произошла непредвиденная ошибка: ...»

Применяется ко всем операциям в `core.py`. Дублирующие `try...except` из `core` удалены.

### `confirm_action(action_name)`

Фабрика декораторов: перед опасной операцией спрашивает
`Вы уверены, что хотите выполнить "<action_name>"? [y/n]:`.
Любой ответ, кроме `y`, отменяет операцию.

Применяется к `drop_table` и `delete`.

### `log_time`

Замеряет время выполнения через `time.monotonic()` и печатает:
`Функция <имя> выполнилась за X.XXX секунд.`

Применяется к `select` и `insert`.

### `create_cacher()`

Возвращает функцию `cache_result(key, value_func)` с кэшем в замыкании.
Используется в `select`: одинаковые запросы (по содержимому данных и `where`) возвращаются из кэша.

### Пример

```
>>>Введите команду: delete from users where ID = 1
Вы уверены, что хотите выполнить "удаление записей"? [y/n]: n
Операция отменена.

>>>Введите команду: delete from users where ID = 1
Вы уверены, что хотите выполнить "удаление записей"? [y/n]: y
Запись с ID=1 успешно удалена из таблицы "users".

>>>Введите команду: select from users
Функция select выполнилась за 0.000 секунд.
+----+--------+-----+-----------+
...
```

## 1-ое Демо работы проекта на asciinema.org

https://asciinema.org/a/AlOqbIHD7Bf3jSm2

## 2-ое Демо работы проекта на asciinema.org (CRUD-операции)

https://asciinema.org/a/y9mwtcD2Zd9fCC62

## 3-e Демо работы (В проекте реализованы декораторы)

https://asciinema.org/a/hmn0JDNiL2YAuZ4m

## Финальное Демо работы (Тестирование и завершение проекта)

https://asciinema.org/a/T114lEE93gsQbwRK
