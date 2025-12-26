# TODO-лист (hometask-8) — HTTP сервер на чистой стандартной библиотеке Python

## О проекте

Это учебный проект: **HTTP-сервер, который управляет списком задач пользователя (TODO)**.

Ключевая идея проекта — **самописный мини-фреймворк веб-сервера**, реализованный **только на стандартной библиотеке Python** (без FastAPI/Flask/Django и без сторонних HTTP-библиотек).

Сервер умеет:
- принимать **HTTP-запросы** (GET/POST/PUT),
- маршрутизировать запросы через **Routers** «как в FastAPI»,
- внедрять зависимости через **Dependency Injection** (`Depends()`),
- сохранять задачи в файл **JSON** и восстанавливать их при старте.

## Требования
- Python **3.11+** (проект проверялся на 3.13)

Сторонние зависимости **не нужны**.

## Конфигурация

Проект читает конфиг из JSON-файла. Путь задаётся переменной окружения `CONFIG_PATH`.

Пример конфига лежит здесь:
- `config/config.json`

Основные поля:
- `api.host` / `api.port` — на каком адресе слушать сервер
- `api.root_path` — префикс API (обычно `/tasks`)
- `database.directory` / `database.storage_name` — куда сохранять задачи

По умолчанию задачи сохраняются в файл:
- `storage/0/tasks.json`

## Запуск

Запуск из корня проекта:

```bash
CONFIG_PATH=./config/config.json python -m server.main
```

После запуска сервер будет слушать:
- `http://127.0.0.1:8000` (по умолчанию)

## API (эндпоинты)

### 1) Проверка здоровья

- `GET /tasks/health`

### 2) Получить список задач

- `GET /tasks/get`

Возвращает JSON-массив задач:

```json
[
  {"title":"Gym","id":1,"priority":"low","isDone":false},
  {"title":"Buy a laptop","id":2,"priority":"high","isDone":true}
]
```

### 3) Создать задачу

- `POST /tasks/create`

Тело запроса (JSON):
- `title`: строка
- `priority`: `"low" | "normal" | "high"`

Сервер создаёт задачу, выставляет `isDone=false`, выдаёт уникальный `id`, и возвращает созданную сущность.

### 4) Отметить задачу выполненной

- `PUT /tasks/{id}/complete`

Если задача существует — **200** и пустое тело.  
Если задачи нет — **404**.

## Примеры curl (проверка вручную)

### Healthcheck

```bash
curl -i 'http://127.0.0.1:8000/tasks/health'
```

### Создать задачу

```bash
curl -i -X POST 'http://127.0.0.1:8000/tasks/create' \
  -H 'content-type: application/json' \
  -d '{"title":"Gym","priority":"low"}'
```

### Получить список

```bash
curl -i 'http://127.0.0.1:8000/tasks/get'
```

### Отметить выполненной

```bash
curl -i -X PUT 'http://127.0.0.1:8000/tasks/1/complete'
```

### Проверить 404 (несуществующий id)

```bash
curl -i -X PUT 'http://127.0.0.1:8000/tasks/999/complete'
```
