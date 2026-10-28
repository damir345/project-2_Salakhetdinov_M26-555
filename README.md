# project-2_Salakhetdinov_M26-555
Домашнее задание №2. Примитивная база данных

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

## 1-ое Демо работы проекта на asciinema.org

https://asciinema.org/a/AlOqbIHD7Bf3jSm2

## 2-ое Демо работы проекта на asciinema.org (CRUD-операции)

https://asciinema.org/a/y9mwtcD2Zd9fCC62
