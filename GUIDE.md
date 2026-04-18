# Полный гайд по проекту "Password Manager API"

Учебный проект на **FastAPI + SQLAlchemy + PostgreSQL** — бэкенд менеджера паролей.
Гайд написан с нуля: от синтаксиса Python до того, как веб-сервер превращает HTTP-запрос в запись в БД.

---

# Оглавление

1. [Что такое этот проект](#1-что-такое-этот-проект)
2. [Python-основы, которые нужны](#2-python-основы-которые-нужны)
3. [Асинхронность: `async` / `await`](#3-асинхронность-async--await)
4. [Декораторы](#4-декораторы)
5. [Как работает веб и API](#5-как-работает-веб-и-api)
6. [FastAPI — фреймворк для API](#6-fastapi--фреймворк-для-api)
7. [Pydantic — валидация входа/выхода](#7-pydantic--валидация-входавыхода)
8. [SQLAlchemy — ORM для БД](#8-sqlalchemy--orm-для-бд)
9. [Архитектура проекта: слои](#9-архитектура-проекта-слои)
10. [Путь HTTP-запроса через все слои](#10-путь-http-запроса-через-все-слои)
11. [Разбор сущностей проекта](#11-разбор-сущностей-проекта)
12. [Безопасность (Лаба №3)](#12-безопасность-лаба-3)
13. [Обработка ошибок](#13-обработка-ошибок)
14. [Запуск и тестирование](#14-запуск-и-тестирование)
15. [HTTP-коды ответов](#15-http-коды-ответов)
16. [Шпаргалка-словарик](#16-шпаргалка-словарик)

---

# 1. Что такое этот проект

**Менеджер паролей** — программа, в которой пользователь хранит свои пароли, защищённые одним главным паролем (master password). Похоже на Bitwarden, 1Password, LastPass.

Архитектура менеджера паролей специфична: **сервер не знает паролей пользователя**. Все пароли шифруются на клиенте ключом, который получается из master password. Сервер хранит только зашифрованные строки и ничего не может с ними сделать без master password.

Наш проект — **серверная часть (API)**. Это значит:
- Мы принимаем HTTP-запросы от клиента (веб-интерфейса, мобильного приложения).
- Храним в БД зашифрованные данные: пароли, заметки, карты и т.п.
- Отдаём обратно, когда клиент попросит.
- Сами расшифровать ничего не можем — у нас нет ключа.

**Стек технологий:**
- **FastAPI** — веб-фреймворк, превращает Python-функции в HTTP-эндпоинты.
- **Pydantic** — валидирует входные JSON и описывает выходные.
- **SQLAlchemy (async)** — ORM, общается с БД через Python-классы.
- **PostgreSQL** — реляционная БД, лежит в Docker.
- **Uvicorn** — ASGI-сервер, который запускает FastAPI.

---

# 2. Python-основы, которые нужны

## 2.1. Типы данных

```python
x = 5                  # int — целое число
y = 3.14               # float — дробное
s = "привет"           # str — строка
b = True               # bool — True/False
none = None            # None — "ничего нет"
lst = [1, 2, 3]        # list — список
tpl = (1, 2, 3)        # tuple — неизменяемый список
dct = {"a": 1, "b": 2} # dict — словарь (ключ → значение)
```

## 2.2. Функции

```python
def add(a, b):
    return a + b

result = add(2, 3)   # 5
```

**Параметры по умолчанию:**
```python
def greet(name="друг"):
    return f"Привет, {name}"
```

**`*args` и `**kwargs`** — произвольное количество аргументов:
```python
def f(*args, **kwargs):
    # args — кортеж позиционных, kwargs — словарь именованных
    ...

f(1, 2, 3, a=10, b=20)
# args = (1, 2, 3)
# kwargs = {"a": 10, "b": 20}
```

**Распаковка словаря в аргументы (`**`):**
```python
data = {"name": "Вася", "age": 30}
User(**data)   # то же самое, что User(name="Вася", age=30)
```
Именно так мы создаём ORM-объекты из Pydantic-данных: `User(**data.model_dump())`.

## 2.3. Классы

```python
class User:
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Привет, {self.name}"

u = User("Вася")
u.greet()   # "Привет, Вася"
```

**Наследование:**
```python
class Base:
    pass

class User(Base):
    ...
```
`User` — это `Base` плюс своё. В нашем проекте все ORM-модели наследуются от `Base`.

## 2.4. f-строки

```python
name = "Вася"
print(f"Привет, {name}")   # "Привет, Вася"
```
Префикс `f` включает подстановку выражений внутри `{}`.

**Осторожно:** f-строки в SQL — это инъекция:
```python
sql = f"SELECT * FROM users WHERE name = '{name}'"  # ОПАСНО
```

## 2.5. Аннотации типов

```python
def add(a: int, b: int) -> int:
    return a + b
```
Python **не проверяет** эти типы сам (это не Java/C#). Но Pydantic, FastAPI, IDE — читают и используют.

**Union (`|`):**
```python
x: int | None = None   # либо int, либо None
```
Этот синтаксис появился в Python 3.10. Раньше писали `Optional[int]` / `Union[int, None]`.

## 2.6. Списковые и словарные включения

```python
[x * 2 for x in range(5)]          # [0, 2, 4, 6, 8]
[x for x in nums if x > 0]         # только положительные
{k: v for k, v in d.items()}       # dict comprehension
```

В проекте используется в обработчике валидации:
```python
details = [
    {"field": ".".join(str(x) for x in e["loc"][1:]), "error": e["msg"]}
    for e in exc.errors()
]
```

## 2.7. Lambda (анонимная функция)

```python
add = lambda a, b: a + b
add(2, 3)   # 5
```
В проекте используется в `default=lambda: datetime.now(timezone.utc)` — чтобы функция **вызывалась при создании каждой записи**, а не один раз при старте программы.

Если написать `default=datetime.now(timezone.utc)` (без lambda) — значение вычислится один раз, и все записи получат одно и то же время.

## 2.8. Context manager (`with`)

```python
with open("file.txt") as f:
    data = f.read()
# файл автоматически закрыт
```
`async with` — то же самое, но асинхронное.

В `get_db()`:
```python
async with AsyncSessionLocal() as session:
    yield session
# после yield сессия закроется
```

## 2.9. `yield` и генераторы

```python
def counter():
    yield 1
    yield 2
    yield 3

for x in counter():   # 1, 2, 3
    print(x)
```

`yield` приостанавливает функцию и возвращает значение. Следующий вызов продолжит с того же места.

В FastAPI `Depends(get_db)` использует генератор: код до `yield` = setup, код после = teardown.

---

# 3. Асинхронность: `async` / `await`

## 3.1. Зачем вообще асинхронность

Обычный код **блокирующий**: пока запрос к БД идёт (например, 50 мс), Python просто ждёт и ничего другого делать не может. Если к серверу обратились 100 человек одновременно — все по очереди ждут.

Асинхронный код: пока один запрос ждёт БД, Python берёт и обрабатывает другой. Один процесс обслуживает тысячи параллельных запросов.

## 3.2. Как это выглядит

```python
async def get_user(db):
    result = await db.execute(...)
    return result
```

- `async def` — объявляет **корутину** (особую функцию, которая умеет приостанавливаться).
- `await` — точка, где функция может уступить место другим. Означает "жди этот результат, но не блокируй всё".

## 3.3. Важное правило

- `await` можно писать **только внутри `async def`**.
- `async def` **возвращает корутину**, а не результат. Чтобы получить результат — либо `await`, либо запустить event loop.

```python
async def f():
    return 42

f()          # <coroutine object f>  — корутина, не запущенная
await f()    # 42 (только внутри другой async def)
```

## 3.4. Event loop

Это "расписание": машина, которая переключается между корутинами. В FastAPI event loop запускает Uvicorn — тебе его запускать не надо, он создаётся автоматически.

## 3.5. Весь стек — async

В нашем проекте **всё** асинхронно:
- Роутеры: `async def get_users(...)`.
- Сервисы: `async def create(...)`.
- БД-драйвер: `asyncpg` (не `psycopg2`).
- Движок SQLAlchemy: `create_async_engine` (не `create_engine`).
- Сессия: `AsyncSession` (не `Session`).

Если где-то синхронный вызов — вся цепочка блокируется.

---

# 4. Декораторы

## 4.1. Суть

Декоратор — функция, которая принимает другую функцию и возвращает (обычно модифицированную) функцию.

```python
def my_decorator(func):
    def wrapper():
        print("до")
        func()
        print("после")
    return wrapper

@my_decorator
def hello():
    print("привет")

hello()
# до
# привет
# после
```

`@my_decorator` над `hello` — это сахар для `hello = my_decorator(hello)`.

## 4.2. Декораторы в нашем проекте

**FastAPI роут:**
```python
@router.get("/users/")
async def get_users():
    ...
```
`router.get("/users/")` **регистрирует** функцию как обработчик GET-запроса на `/users/`. Сама функция остаётся прежней, но FastAPI запоминает: "для пути `/users/` зови `get_users`".

**Startup:**
```python
@app.on_event("startup")
async def startup():
    ...
```
"Вызови эту функцию, когда приложение запустится".

**Exception handler:**
```python
@app.exception_handler(HTTPException)
async def http_handler(request, exc):
    ...
```
"Если где-то вылетит `HTTPException`, перехвати и вызови эту функцию".

---

# 5. Как работает веб и API

## 5.1. HTTP

Протокол общения браузера с сервером. Клиент посылает **запрос**, сервер — **ответ**.

**Запрос** состоит из:
- Метода: `GET`, `POST`, `PUT`, `DELETE`, `PATCH`.
- URL: `/api/users/123`.
- Заголовков: `Content-Type: application/json`, `Authorization: Bearer ...`.
- Тела (не у всех методов): обычно JSON.

**Ответ:**
- Статус-код: `200 OK`, `404 Not Found`, `500 Internal Server Error` и т.д.
- Заголовков.
- Тела (JSON, HTML, что угодно).

## 5.2. Методы и их смысл

| Метод   | Для чего                          | Идемпотентный? |
|---------|-----------------------------------|----------------|
| GET     | Получить                          | Да             |
| POST    | Создать                           | Нет            |
| PUT     | Заменить целиком                  | Да             |
| PATCH   | Частично обновить                 | Нет/да         |
| DELETE  | Удалить                           | Да             |

Идемпотентный = повторное выполнение даёт тот же результат.

## 5.3. REST

Стиль API, где:
- Каждый ресурс (например, пользователь) имеет URL: `/users/`, `/users/{id}`.
- Операция определяется HTTP-методом, а не URL.

Примеры:
- `GET /api/users/` — список всех.
- `GET /api/users/42` — один.
- `POST /api/users/` — создать.
- `PUT /api/users/42` — обновить.
- `DELETE /api/users/42` — удалить.

## 5.4. JSON

Формат обмена данными. Выглядит как Python-словарь:
```json
{"id": 42, "name": "Вася", "emails": ["a@b.c"]}
```
FastAPI автоматически сериализует Python-объекты в JSON и десериализует JSON в Python.

---

# 6. FastAPI — фреймворк для API

## 6.1. Основной объект

```python
from fastapi import FastAPI
app = FastAPI()
```
`app` — это веб-приложение. К нему подключаются роутеры, обработчики, middleware.

## 6.2. Роутер

```python
from fastapi import APIRouter
router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("/")
async def list_users():
    ...
```

- `prefix` — префикс путей: все пути внутри роутера получат `/api/users` в начале.
- `tags` — группировка в Swagger-документации.

Роутеры **подключаются к приложению** в `main.py`:
```python
app.include_router(users.router)
```

## 6.3. Параметры пути и запроса

**Путь:**
```python
@router.get("/{user_id}")
async def get(user_id: uuid.UUID):
    ...
```
`{user_id}` в URL → параметр функции. FastAPI сам конвертирует строку в `uuid.UUID` (и выдаст 400, если не UUID).

**Query-параметр:**
```python
from fastapi import Query
@router.get("/search")
async def search(q: str = Query(..., min_length=1)):
    ...
```
URL: `/search?q=hello`.

**Тело (body):**
```python
async def create(data: UserCreate):
    ...
```
Если параметр — Pydantic-модель, FastAPI берёт JSON из тела, валидирует и кладёт в `data`.

## 6.4. Dependency Injection (`Depends`)

```python
async def get_users(db: AsyncSession = Depends(get_db)):
    ...
```

`Depends(get_db)` говорит: "перед вызовом этой функции вызови `get_db()`, результат подставь в параметр `db`".

`get_db` — генератор:
```python
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

Как это работает:
1. FastAPI вызывает `get_db()`.
2. Доходит до `yield session` — FastAPI забирает `session` и передаёт в функцию.
3. После ответа клиенту FastAPI возвращается в `get_db` — срабатывает `async with` → сессия закрывается.

Это гарантирует, что сессия всегда закроется, даже при ошибке.

## 6.5. `response_model`, `status_code`

```python
@router.post("/", response_model=UserResponse, status_code=201)
async def create(data: UserCreate):
    return user  # user — это объект SQLAlchemy
```

- `response_model=UserResponse` — FastAPI возьмёт возвращённый объект, отфильтрует поля (только те, что есть в `UserResponse`), сконвертирует в JSON. Если `user` содержит `master_password_hash`, но в `UserResponse` этого поля нет — он не попадёт в ответ. **Защита от утечки данных.**
- `status_code=201` — HTTP-код успешного ответа (201 Created для POST).

## 6.6. Swagger (OpenAPI)

FastAPI автоматически генерирует документацию из кода. Зайди на `http://127.0.0.1:8000/docs` — там:
- Список всех эндпоинтов.
- Какие параметры они принимают.
- Какие ответы возвращают.
- Прямо там можно нажать "Try it out" и отправить запрос.

Всё это берётся из твоих Pydantic-схем и сигнатур функций.

---

# 7. Pydantic — валидация входа/выхода

## 7.1. Схема

```python
from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    kdf_iterations: int = Field(..., ge=1000, le=2_000_000)
```

Pydantic при получении JSON:
1. Парсит JSON → словарь.
2. По каждому полю проверяет тип и ограничения.
3. Если всё ок — создаёт объект `UserCreate`.
4. Если нет — кидает `RequestValidationError`, FastAPI превращает в 400.

## 7.2. `Field`

Добавляет правила к полю:

| Параметр      | Смысл                                             |
|---------------|---------------------------------------------------|
| `...`         | Обязательное поле (не имеет default)              |
| `default`     | Значение по умолчанию                             |
| `min_length`  | Минимальная длина (строки/списка)                 |
| `max_length`  | Максимальная длина                                |
| `ge`          | Greater or equal (`>=`) — для чисел               |
| `le`          | Less or equal (`<=`)                              |
| `gt`, `lt`    | Строго `>`, `<`                                   |
| `pattern`     | Regex, которому строка должна соответствовать     |
| `description` | Текст для Swagger                                 |

## 7.3. Специальные типы

- `EmailStr` — валидный email (требует `pydantic[email]`).
- `uuid.UUID` — валидный UUID.
- `datetime` — ISO 8601 даты.
- `str | None` — поле может быть строкой или отсутствовать.

## 7.4. Три типа схем на сущность

**Create** — что клиент прислал для создания:
```python
class UserCreate(BaseModel):
    email: EmailStr
    master_password_hash: str
    ...  # всё обязательное
```

**Update** — что можно обновить (все поля опциональные):
```python
class UserUpdate(BaseModel):
    name: str | None = None
    premium: bool | None = None
```

**Response** — что отдаём клиенту (без чувствительных полей):
```python
class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str
    # master_password_hash НЕ здесь — в ответе его не будет

    class Config:
        from_attributes = True
```

`from_attributes = True` разрешает Pydantic читать данные не из dict, а из атрибутов объекта (у нас — из ORM-модели).

## 7.5. `model_dump`

Метод превращает Pydantic-модель обратно в словарь.

```python
data = UserCreate(email="a@b.c", name="Вася", ...)
data.model_dump()
# {"email": "a@b.c", "name": "Вася", ...}
```

`exclude_unset=True` — вернуть **только те поля, которые клиент реально прислал**:
```python
for field, value in data.model_dump(exclude_unset=True).items():
    setattr(user, field, value)
```
Если клиент не прислал `name`, мы не перезапишем его на `None` — оставим старое.

---

# 8. SQLAlchemy — ORM для БД

## 8.1. Зачем ORM

Без ORM код выглядит так:
```python
cursor.execute("SELECT id, name FROM users WHERE id = %s", (user_id,))
row = cursor.fetchone()
```
Это работает, но:
- Легко сделать SQL-инъекцию, если забыть параметризацию.
- Типы конвертируются вручную.
- Много шаблонного кода.

С ORM:
```python
user = await db.execute(select(User).where(User.id == user_id))
```
SQL генерируется автоматически, параметры всегда биндятся безопасно, типы конвертируются.

## 8.2. Модель

```python
class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    ...
```

- `__tablename__` — имя таблицы в БД.
- `Column(...)` — колонка со своим типом и ограничениями.
- `primary_key=True` — первичный ключ.
- `unique=True` — уникальное значение.
- `nullable=False` — NOT NULL.
- `default=...` — значение по умолчанию (на уровне ORM).
- `ForeignKey("users.id")` — внешний ключ на `users.id`.

## 8.3. Движок и сессия

**Движок** — соединение с БД:
```python
engine = create_async_engine("postgresql+asyncpg://root:root@localhost:5432/postgres")
```
Формат URL: `<диалект>+<драйвер>://<user>:<password>@<host>:<port>/<database>`.

**Сессия** — "рабочий контекст" для набора операций:
```python
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

Сессия знает про загруженные объекты, отслеживает изменения, коммитит транзакцию.
`expire_on_commit=False` — после `commit` объекты остаются "живыми" и их поля можно читать (иначе SQLAlchemy помечает их устаревшими).

## 8.4. Типичные операции

**Получить всех:**
```python
result = await db.execute(select(User))
users = result.scalars().all()
```
`scalars()` — извлечь первую колонку каждой строки (то есть сами объекты `User`).

**Получить одного:**
```python
result = await db.execute(select(User).where(User.id == user_id))
user = result.scalar_one_or_none()
# вернёт объект или None
```

**Создать:**
```python
user = User(email="a@b.c", ...)
db.add(user)
await db.commit()
await db.refresh(user)   # подгрузить поля, сгенерированные БД (id, created_at)
```

**Обновить:**
```python
user = await get_by_id(db, user_id)
user.name = "new name"
await db.commit()
```
Сессия сама замечает, что атрибут поменялся, и генерирует `UPDATE`.

**Удалить:**
```python
await db.delete(user)
await db.commit()
```

## 8.5. `text()` — сырой SQL

Когда нужно написать SQL вручную:
```python
from sqlalchemy import text
sql = text("SELECT id, email FROM users WHERE name = :q")
result = await db.execute(sql, {"q": q})
```

- `text(...)` оборачивает строку в "это готовый SQL".
- `:q` — плейсхолдер, значение подставляется через словарь — **безопасно**.
- В SQLAlchemy 2.0 `db.execute("голая строка")` не работает: либо ORM-конструкция (`select(...)`), либо `text(...)`.

## 8.6. `create_all`

```python
await conn.run_sync(Base.metadata.create_all)
```
Создаёт **все таблицы, которых ещё нет** в БД. Существующие не трогает, изменения в схеме **не подхватывает**. Для реальных изменений нужен Alembic (миграции).

Если поменял модель — нужно либо пересоздать БД (`docker-compose down -v`), либо писать миграцию.

---

# 9. Архитектура проекта: слои

```
HTTP-запрос
    ↓
Router (routers/*.py) — принимает запрос, проверяет URL/метод
    ↓
Pydantic (schemas/*.py) — валидирует входные данные
    ↓
Service (services/*.py) — бизнес-логика, работа с БД
    ↓
Model (models/*.py) — структура таблицы, ORM-объект
    ↓
PostgreSQL
```

И обратно:
```
PostgreSQL → ORM-объект → response_model (Pydantic) → JSON → клиент
```

## 9.1. Model (`app/models/`)

Описывает **таблицу в БД**. Один класс = одна таблица.

```python
class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True)
    ...
```

**Зачем:** чтобы с БД общаться через Python-объекты, а не SQL-строки.

## 9.2. Schema (`app/schemas/`)

Описывает **форму JSON** для API. Три класса на сущность: `Create`, `Update`, `Response`.

**Зачем:**
- Валидирует вход (что клиент прислал).
- Ограничивает выход (какие поля отдавать).
- Описывает Swagger.

**Model ≠ Schema:** модель — БД, схема — API. У них могут быть разные поля.

## 9.3. Service (`app/services/`)

**Бизнес-логика**: создать, найти, обновить, удалить. Только операции с данными, без HTTP.

```python
async def create(db: AsyncSession, data: UserCreate):
    user = User(**data.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
```

**Зачем:** отделить "что делаем с данными" от "как принимаем запрос". Завтра появится gRPC — роутеры поменяем, сервисы останутся.

## 9.4. Router (`app/routers/`)

Связывает URL с сервисом. Читает запрос, вызывает сервис, возвращает ответ.

```python
@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await user_service.create(db, data)
```

**Зачем:** понимает HTTP-протокол, а сервис о HTTP ничего не знает.

## 9.5. `main.py`

Собирает всё вместе:
```python
app = FastAPI()
register_exception_handlers(app)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(users.router)
app.include_router(folders.router)
# ...
```

---

# 10. Путь HTTP-запроса через все слои

Клиент шлёт: `POST /api/users/` с JSON:
```json
{
  "email": "test@example.com",
  "name": "Вася",
  "master_password_hash": "$2b$12$...",
  "kdf_type": 0,
  "kdf_iterations": 100000
}
```

## Шаг 1. Uvicorn принимает TCP-запрос

Парсит HTTP: метод `POST`, URL `/api/users/`, тело как байты.

## Шаг 2. FastAPI матчит роут

Ищет функцию, зарегистрированную на `POST /api/users/` → находит `create_user` в `routers/users.py`.

## Шаг 3. Разрешает зависимости

У `create_user` параметр `db: AsyncSession = Depends(get_db)`. FastAPI:
1. Вызывает `get_db()`.
2. Доходит до `yield session`.
3. Подставляет `session` в `db`.

## Шаг 4. Валидирует тело

Второй параметр — `data: UserCreate`. FastAPI:
1. Парсит JSON.
2. Создаёт `UserCreate(**json_data)`.
3. Pydantic проверяет все поля.
4. Если валидно — передаёт в функцию. Если нет — `RequestValidationError` → 400.

## Шаг 5. Вызов функции

```python
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await user_service.create(db, data)
```

## Шаг 6. Сервис создаёт объект

```python
async def create(db, data):
    user = User(**data.model_dump())   # создаём ORM-модель
    db.add(user)                       # добавляем в сессию
    await db.commit()                  # COMMIT → данные в БД
    await db.refresh(user)             # подгружаем id, created_at
    return user
```

## Шаг 7. Возврат через `response_model`

Функция возвращает объект `User`. FastAPI смотрит `response_model=UserResponse`:
1. Читает только те поля, что перечислены в `UserResponse`.
2. Конвертирует в JSON.
3. Отдаёт клиенту со статусом 201.

## Шаг 8. Закрытие сессии

FastAPI возвращается в `get_db`, срабатывает выход из `async with` → `session.close()`.

---

# 11. Разбор сущностей проекта

Всего в проекте **10 сущностей**. Разберём по порядку.

## 11.1. User — пользователь

**Таблица:** `users` (`app/models/user.py`)

| Поле                   | Тип       | Смысл                                          |
|------------------------|-----------|------------------------------------------------|
| `id`                   | UUID      | Первичный ключ                                 |
| `email`                | str       | Уникальный email                               |
| `name`                 | str       | Отображаемое имя                               |
| `master_password_hash` | str       | **Хэш** master password (bcrypt/argon2)        |
| `master_password_hint` | str       | Подсказка для master password                  |
| `kdf_type`             | int       | Тип KDF (0 — PBKDF2, 1 — Argon2 и т.п.)        |
| `kdf_iterations`       | int       | Количество итераций KDF                        |
| `two_factor_enabled`   | bool      | Включён ли 2FA                                 |
| `email_verified`       | bool      | Подтверждён ли email                           |
| `security_stamp`       | str?      | Штамп для инвалидации токенов                  |
| `premium`              | bool      | Платный ли аккаунт                             |
| `created_at`           | datetime  | Дата создания                                  |
| `updated_at`           | datetime  | Дата последнего обновления                     |

**Важно о master password:**
- На сервере хранится **ТОЛЬКО хэш** (необратимое преобразование).
- Сервер никогда не видит plain-text пароль.
- KDF (Key Derivation Function) делает хэширование медленным — защита от перебора.
- `kdf_iterations` регулирует, насколько медленно. Больше итераций — труднее подобрать пароль.

## 11.2. Folder — папка для шифров

**Таблица:** `folders`

Пользователь может группировать свои пароли по папкам. Имя папки зашифровано (сервер не знает "Работа" / "Личное").

| Поле             | Тип      | Смысл                         |
|------------------|----------|-------------------------------|
| `id`             | UUID     |                               |
| `user_id`        | UUID FK  | Владелец                      |
| `name_encrypted` | TEXT     | Зашифрованное имя             |
| `created_at`     | datetime |                               |
| `updated_at`     | datetime |                               |

## 11.3. Cipher — шифр (основа)

**Таблица:** `ciphers`

Это "запись" в менеджере паролей. Она может быть 4 типов:
1. Login — логин/пароль для сайта.
2. Card — банковская карта.
3. Identity — личность (имя, адрес, телефон...).
4. Secure note — заметка.

У `Cipher` хранятся **общие** поля; специфичные — в отдельных таблицах (`cipher_logins`, `cipher_cards`...).

| Поле              | Тип      | Смысл                              |
|-------------------|----------|------------------------------------|
| `id`              | UUID     |                                    |
| `user_id`         | UUID FK  | Владелец                           |
| `folder_id`       | UUID? FK | Папка (может быть без папки)       |
| `type`            | int      | 1-4 (тип шифра)                    |
| `name_encrypted`  | TEXT     | Зашифрованное название             |
| `notes_encrypted` | TEXT     | Зашифрованные заметки              |
| `favorite`        | bool     | Избранное                          |
| `created_at`      | datetime |                                    |
| `updated_at`      | datetime |                                    |
| `revision_date`   | datetime | Дата последнего редактирования     |

## 11.4. CipherLogin — детали login-шифра

**Таблица:** `cipher_logins`
**PK:** `cipher_id` (one-to-one с `Cipher`)

| Поле                         | Тип           |
|------------------------------|---------------|
| `cipher_id`                  | UUID PK/FK    |
| `username_encrypted`         | TEXT          |
| `password_encrypted`         | TEXT          |
| `totp_encrypted`             | TEXT?         |
| `uris_encrypted`             | JSON          |
| `password_history_encrypted` | JSON?         |

## 11.5. CipherCard — детали карты

**Таблица:** `cipher_cards`
**PK:** `cipher_id`

Поля: `cardholder_name_encrypted`, `brand_encrypted`, `number_encrypted`, `exp_month_encrypted`, `exp_year_encrypted`, `code_encrypted` — все зашифрованы.

## 11.6. CipherIdentity — детали идентичности

**Таблица:** `cipher_identities`
**PK:** `cipher_id`

Поля: `title`, `first_name`, `last_name`, `email`, `phone`, `address`, `ssn` — все `_encrypted`.

## 11.7. CipherField — пользовательские поля

**Таблица:** `cipher_fields`

Дополнительные поля, которые пользователь сам добавил к шифру (например, "Секретный вопрос"). Many-to-one с `Cipher`.

| Поле               | Тип      |
|--------------------|----------|
| `id`               | UUID     |
| `cipher_id`        | UUID FK  |
| `type`             | int      |
| `name_encrypted`   | TEXT     |
| `value_encrypted`  | TEXT     |

## 11.8. Device — устройство пользователя

**Таблица:** `devices`

Хранит устройства, с которых пользователь входил (для refresh-токенов, push-уведомлений).

| Поле             | Тип       | Смысл                          |
|------------------|-----------|--------------------------------|
| `id`             | UUID      |                                |
| `user_id`        | UUID FK   |                                |
| `type`           | int       | Mobile/Desktop/Web...          |
| `name`           | str       | Название устройства            |
| `identifier`     | str       | Уникальный ID устройства       |
| `push_token`     | str?      | Токен для push-уведомлений     |
| `created_at`     | datetime  |                                |
| `last_login_at`  | datetime? |                                |

## 11.9. RefreshToken — токен обновления

**Таблица:** `refresh_tokens`

Используется для обновления access-токенов без повторного ввода пароля.

| Поле         | Тип       |
|--------------|-----------|
| `id`         | UUID      |
| `user_id`    | UUID FK   |
| `device_id`  | UUID FK   |
| `token_hash` | str       |
| `expires_at` | datetime  |
| `created_at` | datetime  |

Хранится **хэш** токена, не сам токен.

## 11.10. AuditLog — журнал событий

**Таблица:** `audit_logs`

Записывает важные события: вход, смена пароля, попытка взлома.

| Поле          | Тип       |
|---------------|-----------|
| `id`          | UUID      |
| `user_id`     | UUID FK   |
| `event_type`  | int       |
| `ip_address`  | str       |
| `device_info` | str       |
| `event_at`    | datetime  |
| `metadata`    | JSON?     |

---

# 12. Безопасность (Лаба №3)

В Лабораторной №3 было 5 требований — все реализованы.

## 12.1. Валидация входных данных

**Где:** `app/schemas/*.py`.

**Как:**
- Pydantic-схемы с `Field(...)` задают правила.
- Обязательность (`...` или `default`).
- Диапазоны (`ge`, `le`) для чисел.
- Длины (`min_length`, `max_length`) для строк.
- Regex (`pattern`) для специфических форматов.
- `EmailStr` для email.
- `uuid.UUID` для идентификаторов.

**Пример:**
```python
class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    kdf_iterations: int = Field(..., ge=1000, le=2_000_000)
```

**Защита от чего:**
- Битые данные (отсутствующие поля → 400).
- Слишком большие значения (DoS через огромные строки).
- Слишком маленькие (слабые параметры безопасности, см. `kdf_iterations`).
- Некорректные форматы (email без `@`, UUID не-UUID).

## 12.2. Обработка ошибок с унифицированным форматом

**Где:** `app/errors.py`.

**Формат ответа при любой ошибке:**
```json
{
  "status": 400,
  "message": "Validation failed",
  "details": [{"field": "email", "error": "value is not a valid email"}]
}
```

**Три обработчика:**
1. `RequestValidationError` → 400 с деталями валидации.
2. `HTTPException` → переформатирует стандартный FastAPI-ответ в наш формат.
3. `SQLAlchemyError` → 500 с **безопасным** сообщением (скрывает детали БД).

**Подробнее:** раздел 13.

## 12.3. Защита от SQL-инъекций

**Где:** все сервисы используют ORM; `app/routers/demo.py` — демонстрация.

**Уязвимый код (для демо):**
```python
@router.get("/vulnerable-search")
async def vulnerable_search(q: str, db: AsyncSession = Depends(get_db)):
    sql = f"SELECT id, email, name FROM users WHERE name = '{q}'"
    result = await db.execute(text(sql))
    return {"query": sql, "rows": [dict(r._mapping) for r in result]}
```
Если `q = "anything' OR 1=1 --"`, запрос вернёт всех пользователей.

**Безопасный код:**
```python
@router.get("/safe-search")
async def safe_search(q: str = Query(..., min_length=1, max_length=255),
                      db: AsyncSession = Depends(get_db)):
    sql = text("SELECT id, email, name FROM users WHERE name = :q")
    result = await db.execute(sql, {"q": q})
    return {"rows": [dict(r._mapping) for r in result]}
```
Параметр `:q` биндится драйвером отдельно от SQL-текста — инъекция невозможна.

**В реальных сервисах** мы всегда пользуемся ORM:
```python
select(User).where(User.email == email)
```
SQLAlchemy сама параметризует.

## 12.4. Документация OpenAPI/Swagger с кодами ответов

**Где:** в роутерах `responses=ERROR_RESPONSES`, в `errors.py` — `ERROR_RESPONSES`.

```python
ERROR_RESPONSES = {
    400: {"description": "Validation failed", "content": _ERROR_EXAMPLE},
    404: {"description": "Not found", "content": _ERROR_EXAMPLE},
    500: {"description": "Internal server error", "content": _ERROR_EXAMPLE},
}
```

В Swagger (`/docs`) рядом с каждым эндпоинтом появляются описания 400/404/500 с примерами.

## 12.5. Защита от чрезмерно больших входных данных

**Где:** схемы и Query-параметры.

- `max_length=255` для обычных строк.
- `max_length=5000` для названий шифров.
- `max_length=20000` для зашифрованных заметок.
- `le=2_000_000` для `kdf_iterations` — предотвращает DoS через огромное количество итераций.

## 12.6. Дополнительные аспекты безопасности (не из лабы, но есть)

**Разделение схем Create / Response:**
Клиент отправляет `master_password_hash` при создании, но в `UserResponse` этого поля нет → никогда не вернётся в ответе. **Защита от утечки** через сами API.

**Zero-knowledge архитектура:**
Все "полезные" поля (пароли, заметки, логины, карты) хранятся **зашифрованными** клиентским ключом. Сервер их никогда не расшифровывает.

**Regex на идентификаторы:**
```python
identifier: str = Field(..., pattern=r"^[A-Za-z0-9_-]+$")
```
Защита от мусора в логах, URL, хранилищах. Defense in depth: даже если где-то потом добавят сырой SQL, regex не пропустит строку с кавычками.

**Безопасные сообщения об ошибках БД:**
Когда ловим `SQLAlchemyError`, не отдаём текст `str(exc)` клиенту — там могут быть имена таблиц, колонок, фрагменты запроса. Возвращаем `"Internal server error"`, детали идут в логи.

---

# 13. Обработка ошибок

## 13.1. Файл `app/errors.py`

```python
def _body(status, message, details=None):
    return {"status": status, "message": message, "details": details or []}
```
Хелпер для единого формата тела ошибки. `details or []` — если `None`, подставит пустой список.

## 13.2. Три обработчика

```python
@app.exception_handler(RequestValidationError)
async def validation_handler(request, exc):
    details = [
        {"field": ".".join(str(x) for x in e["loc"][1:]), "error": e["msg"]}
        for e in exc.errors()
    ]
    return JSONResponse(status_code=400, content=_body(400, "Validation failed", details))
```

**Что делает:**
- Ловит ошибку валидации Pydantic.
- Проходит по всем проблемам (`exc.errors()`).
- Каждая ошибка имеет `"loc"` — путь к полю (`("body", "email")`). Отрезаем первый элемент (`"body"`), склеиваем остальное через точку.
- Отдаёт 400 с полным списком.

```python
@app.exception_handler(HTTPException)
async def http_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content=_body(exc.status_code, str(exc.detail)))
```

**Что делает:**
- Ловит любую `HTTPException`, которую мы сами кидаем (`raise HTTPException(404, "Not found")`).
- Переформатирует в единый формат (иначе FastAPI вернул бы `{"detail": "..."}`).

```python
@app.exception_handler(SQLAlchemyError)
async def db_handler(request, exc):
    return JSONResponse(status_code=500, content=_body(500, "Internal server error"))
```

**Что делает:**
- Ловит любую ошибку SQLAlchemy.
- Возвращает 500, **не раскрывая** деталей (безопасность).

## 13.3. Почему status_code в двух местах

```python
JSONResponse(status_code=exc.status_code, content=_body(exc.status_code, ...))
```

- Первый — **HTTP-статус** самого ответа (строка "HTTP/1.1 404 Not Found").
- Второй — число **внутри JSON-тела**.

Клиент может читать либо HTTP-статус, либо поле `status` из тела. Удобно, когда прокси портит заголовки — статус остаётся в теле.

## 13.4. Как мы кидаем ошибки

```python
@router.get("/{user_id}")
async def get_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    user = await user_service.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

`HTTPException` подхватится `http_handler`'ом → клиент получит:
```json
{"status": 404, "message": "User not found", "details": []}
```

## 13.5. `ERROR_RESPONSES` — для Swagger

```python
ERROR_RESPONSES = {
    400: {"description": "Validation failed", "content": _ERROR_EXAMPLE},
    404: {"description": "Not found", "content": _ERROR_EXAMPLE},
    500: {"description": "Internal server error", "content": _ERROR_EXAMPLE},
}
```

Подключается в роутерах через `responses=ERROR_RESPONSES`. Это **не обработчики**, а описание для OpenAPI — чтобы в Swagger рядом с каждым эндпоинтом были примеры ответов 400/404/500.

Если убрать `ERROR_RESPONSES` из роутеров, обработка ошибок не сломается (она в `register_exception_handlers`). Пропадут только описания в Swagger.

---

# 14. Запуск и тестирование

## 14.1. Предварительные требования

- Python 3.10+ (нужно для `str | None`-синтаксиса).
- Docker Desktop с Docker Compose.
- PyCharm / VS Code (опционально).

## 14.2. Установка зависимостей

```bash
pip install -r requirements.txt
```

## 14.3. Запуск БД

В папке проекта:
```bash
docker-compose up -d
```

Это поднимет PostgreSQL 16 на `localhost:5432` с логином `root:root` и БД `postgres`.

Проверить, что работает:
```bash
docker ps
```

## 14.4. Запуск приложения

```bash
python -m app.main
```

или
```bash
uvicorn app.main:app --reload
```

Должно появиться:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

При старте выполнится `startup` → создастся БД-схема (`create_all`).

## 14.5. Открыть Swagger

Браузер: **http://127.0.0.1:8000/docs**

Там все эндпоинты: пользователи, папки, шифры, устройства, refresh-токены, cipher_logins/cards/identities/fields, audit-логи, demo (SQL-инъекции).

## 14.6. Ручное тестирование

**Создать пользователя:**
`POST /api/users/`
```json
{
  "email": "test@example.com",
  "name": "Вася",
  "master_password_hash": "dummy_hash_for_test",
  "master_password_hint": "my favorite food",
  "kdf_type": 0,
  "kdf_iterations": 100000
}
```

Ответ: 201, объект пользователя с `id`.

**Попробовать SQL-инъекцию:**
`GET /api/demo/vulnerable-search?q=' OR 1=1 --` — вернёт всех пользователей.
`GET /api/demo/safe-search?q=' OR 1=1 --` — вернёт 0 записей (никто не называется `' OR 1=1 --`).

**Получить валидационную ошибку:**
`POST /api/users/` с `email: "not-an-email"` → 400:
```json
{
  "status": 400,
  "message": "Validation failed",
  "details": [{"field": "email", "error": "value is not a valid email address: ..."}]
}
```

## 14.7. Пересоздать БД с нуля

Если поменял модель, `create_all` изменения не подхватит:
```bash
docker-compose down -v      # удалить volume с данными
docker-compose up -d        # поднять чистую БД
python -m app.main          # снова запустить → create_all
```

**Осторожно:** `-v` удаляет все данные.

---

# 15. HTTP-коды ответов

## 1xx — Информационные (редко используются)
- **100 Continue** — продолжайте отправлять.

## 2xx — Успех
- **200 OK** — всё хорошо, ответ в теле.
- **201 Created** — ресурс создан (после POST).
- **202 Accepted** — принято в обработку (но ещё не завершено).
- **204 No Content** — успех, но тела ответа нет (после DELETE).

## 3xx — Перенаправления
- **301 Moved Permanently** — ресурс навсегда переехал.
- **302 Found** — временно переехал.
- **304 Not Modified** — кэш актуален.

## 4xx — Ошибки клиента
- **400 Bad Request** — клиент прислал что-то не то (невалидные данные).
- **401 Unauthorized** — требуется аутентификация.
- **403 Forbidden** — аутентифицирован, но нет прав.
- **404 Not Found** — ресурс не существует.
- **405 Method Not Allowed** — метод не поддерживается (POST на GET-only эндпоинт).
- **409 Conflict** — конфликт (например, email уже занят).
- **422 Unprocessable Entity** — данные валидны по форме, но не по смыслу.
- **429 Too Many Requests** — rate limit превышен.

## 5xx — Ошибки сервера
- **500 Internal Server Error** — любая непредвиденная ошибка на сервере.
- **502 Bad Gateway** — прокси не получил ответа от бэкенда.
- **503 Service Unavailable** — сервер временно недоступен.
- **504 Gateway Timeout** — прокси не дождался ответа от бэкенда.

---

# 16. Шпаргалка-словарик

| Термин                         | Что это                                                               |
|--------------------------------|-----------------------------------------------------------------------|
| **API**                        | Интерфейс программы для других программ                               |
| **REST**                       | Стиль API через HTTP-методы и URL-ресурсы                             |
| **HTTP**                       | Протокол передачи данных в вебе                                       |
| **JSON**                       | Формат представления данных                                           |
| **URL**                        | Адрес ресурса                                                          |
| **Endpoint**                   | Конкретный URL, который API обрабатывает                              |
| **ORM**                        | Прослойка для работы с БД через объекты, а не SQL                     |
| **SQL**                        | Язык запросов к реляционной БД                                        |
| **Инъекция (SQL)**             | Внедрение SQL-кода через пользовательский ввод                        |
| **Параметризация**             | Значения передаются в SQL отдельно от текста — защита от инъекций     |
| **Валидация**                  | Проверка корректности данных                                          |
| **Сериализация**               | Превращение объекта в строку/байты (например, в JSON)                 |
| **Десериализация**             | Обратно                                                                |
| **Аутентификация**             | Проверка, кто ты (логин/пароль)                                       |
| **Авторизация**                | Проверка, что тебе можно делать                                       |
| **Хэш**                        | Необратимое преобразование (из пароля → хэш, обратно нельзя)          |
| **Шифрование**                 | Обратимое преобразование с ключом                                     |
| **KDF**                        | Функция получения ключа из пароля (медленная, чтобы не подобрали)     |
| **JWT**                        | Токен в формате JSON, подписанный сервером                            |
| **Refresh token**              | Долгоживущий токен для получения новых access-токенов                 |
| **Dependency Injection**       | Передача зависимостей через параметры, а не создание внутри           |
| **Middleware**                 | Код, выполняющийся до/после каждого запроса                           |
| **Migration**                  | Изменение схемы БД через версионируемые скрипты                       |
| **Transaction**                | Группа операций в БД "всё или ничего"                                  |
| **Commit**                     | Подтвердить транзакцию — изменения становятся постоянными             |
| **Rollback**                   | Откатить транзакцию                                                    |
| **Async / await**              | Асинхронный код: функция может уступить место другим на время ожидания |
| **Coroutine**                  | То, что возвращает `async def` до `await`                             |
| **Event loop**                 | Механизм, который переключается между корутинами                      |
| **ASGI**                       | Асинхронный интерфейс между веб-сервером и Python-приложением         |
| **Uvicorn**                    | ASGI-сервер, запускает FastAPI                                        |
| **OpenAPI / Swagger**          | Стандарт описания API + UI для тестирования                           |
| **UUID**                       | 128-битный уникальный идентификатор                                   |
| **Primary Key**                | Уникальный идентификатор строки в таблице                             |
| **Foreign Key**                | Ссылка на PK другой таблицы                                           |
| **Index**                      | Структура для быстрого поиска по колонке                              |
| **NOT NULL**                   | Колонка обязана иметь значение                                        |
| **UNIQUE**                     | Значение в колонке не может повторяться                               |
| **CASCADE**                    | Удалил родителя — удалились дочерние записи                           |
| **Defense in depth**           | Многоуровневая защита — несколько рубежей на разных слоях             |
| **Zero-knowledge**             | Сервер не знает данных пользователя (всё шифруется на клиенте)        |

---

**Конец гайда.** Если что-то непонятно — спрашивай конкретный раздел, разберём глубже.
