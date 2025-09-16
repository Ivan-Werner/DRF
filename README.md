# Task Tracker API

Серверное приложение для управления задачами сотрудников.  
Реализовано на **Django + DRF**, база данных — **PostgreSQL**, авторизация — **JWT**.  
Проект покрыт тестами (coverage ~95%), содержит документацию и готов к запуску в Docker.

---

## 🚀 Функционал

- **Аутентификация и роли**:
  - Регистрация пользователей, JWT (access + refresh).
  - Роли: `admin`, `manager`, `user`.
  - Админ может менять роли и управлять всеми пользователями.

- **CRUD**:
  - **Users** (для админов).
  - **Employees** (CRUD для менеджеров/админов, просмотр — всем).
  - **Tasks** (CRUD для менеджеров/админов, просмотр — всем).

- **Специальные эндпоинты**:
  - `busy-employees` — сотрудники, отсортированные по количеству активных задач.
  - `important-tasks` — задачи, от которых зависят другие в работе + кандидаты на исполнение.

- **Автодокументация API**: Swagger + ReDoc.

- **Тесты**: покрытие > 75% (сейчас ~95%).

---

## ⚙️ Установка и запуск

### 1. Клонировать репозиторий
```bash
git clone <repo_url>
cd TaskTracker




Создать виртуальное окружение и активировать

python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate


Установить зависимости
pip install -r requirements.txt




В корне проекта создайте файл .env:

DJANGO_SECRET_KEY=replace_me_with_random_string
DEBUG=True

DB_NAME=tasktracker
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=127.0.0.1
DB_PORT=5432


Применить миграции и создать суперпользователя
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

Запустить сервер разработки
python manage.py runserver


coverage run manage.py test
coverage report
coverage html





Работа с проектом


Регистрация → вход → кто я
1.1 Регистрация
URL: POST /api/auth/register/

Body:
{
  "username": "ivan",
  "password": "Qwerty123!@#",
  "email": "ivan@example.com",
  "first_name": "Иван",
  "last_name": "Иванов"
}

Ответ 201:
{
  "id": 2,
  "username": "ivan",
  "email": "ivan@example.com",
  "first_name": "Иван",
  "last_name": "Иванов",
  "role": "user"
}


1.2 Получить токены (логин)
URL: POST /api/auth/token/

Body:
{ "username": "ivan", "password": "Qwerty123!@#" }


Ответ 200:
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6..."
}


1.3 Обновить access-токен
URL: POST /api/auth/token/refresh/
Body:

{ "refresh": "<refresh_token_from_login>" }


Ответ 200:

{ "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6..." }


1.4 Текущий пользователь
URL: GET /api/auth/me/
Headers: Authorization: Bearer <access_token>
Ответ 200:

{
  "id": 2,
  "username": "ivan",
  "email": "ivan@example.com",
  "first_name": "Иван",
  "last_name": "Иванов",
  "role": "user"
}



2) Пользователи (для админа; CRUD)
База: /api/auth/users/


2.1 Список пользователей (только админ)
URL: GET /api/auth/users/
Headers: Authorization: Bearer <admin_access>
Ответ 200 (пример):

[
  {"id":1,"username":"admin","email":"admin@ex.com","first_name":"","last_name":"","role":"admin"},
  {"id":2,"username":"ivan","email":"ivan@example.com","first_name":"Иван","last_name":"Иванов","role":"user"}
]



2.2 Создать пользователя (только админ)
URL: POST /api/auth/users/
Headers: Authorization: Bearer <admin_access>
Body:

{
  "username": "petr",
  "email": "petr@example.com",
  "first_name": "Пётр",
  "last_name": "Петров",
  "role": "manager",
  "password": "Qwerty123!@#"
}


Ответ 201:

{
  "id": 3,
  "username": "petr",
  "email": "petr@example.com",
  "first_name": "Пётр",
  "last_name": "Петров",
  "role": "manager"
}


2.3 Получить пользователя

URL: GET /api/auth/users/3/
Headers: Authorization: Bearer <access>
Ответ 200:

{
  "id": 3,
  "username": "petr",
  "email": "petr@example.com",
  "first_name": "Пётр",
  "last_name": "Петров",
  "role": "manager"
}


2.4 Частично обновить (PATCH)
URL: PATCH /api/auth/users/3/
Headers: Authorization: Bearer <admin_access>
Body (смена роли):

{ "role": "admin" }


Ответ 200: как в GET, с обновлённой ролью.


2.5 Удалить
URL: DELETE /api/auth/users/3/
Headers: Authorization: Bearer <admin_access>
Ответ 204: без тела.



3) Сотрудники (Employees; менеджер/админ меняют, все читают)

База: /api/employees/
Модель: {id, full_name, position}

3.1 Создать сотрудника
URL: POST /api/employees/
Headers: Authorization: Bearer <manager_or_admin_access>
Body:

{ "full_name": "Иванов Иван", "position": "Разработчик" }


Ответ 201:

{ "id": 1, "full_name": "Иванов Иван", "position": "Разработчик" }

3.2 Список сотрудников
URL: GET /api/employees/
Headers: Authorization: Bearer <access>
Ответ 200 (пример):

[
  { "id": 1, "full_name": "Иванов Иван", "position": "Разработчик" }
]

3.3 Обновить сотрудника
URL: PATCH /api/employees/1/
Headers: Authorization: Bearer <manager_or_admin_access>
Body:

{ "position": "Старший разработчик" }


Ответ 200:

{ "id": 1, "full_name": "Иванов Иван", "position": "Старший разработчик" }



4) Задачи (Tasks; менеджер/админ меняют, все читают)
База: /api/tasks/
Статусы: new, in_progress, done, blocked
executor — это ID сотрудника (/api/employees/{id}/)

4.1 Создать задачу
URL: POST /api/tasks/
Headers: Authorization: Bearer <manager_or_admin_access>
Body:

{
  "title": "Подготовить отчёт по спринту",
  "description": "Собрать статусы и риски",
  "parent": null,
  "executor": 1,
  "due_date": "2025-09-22",
  "status": "new"
}


Ответ 201 (пример):

{
  "id": 10,
  "title": "Подготовить отчёт по спринту",
  "description": "Собрать статусы и риски",
  "parent": null,
  "executor": 1,
  "due_date": "2025-09-22",
  "status": "new",
  "status_display": "Новая"
}

4.2 Список задач
URL: GET /api/tasks/
Headers: Authorization: Bearer <access>
Ответ 200 (пример):

[
  {
    "id": 10,
    "title": "Подготовить отчёт по спринту",
    "description": "Собрать статусы и риски",
    "parent": null,
    "executor": 1,
    "due_date": "2025-09-22",
    "status": "new",
    "status_display": "Новая"
  }
]

4.3 Обновить задачу (назначить исполнителя и запустить)
URL: PATCH /api/tasks/10/
Headers: Authorization: Bearer <manager_or_admin_access>
Body:

{ "executor": 1, "status": "in_progress" }


Ответ 200: объект задачи с обновлениями.

4.4 Завершить задачу
URL: PATCH /api/tasks/10/
Headers: Authorization: Bearer <manager_or_admin_access>
Body:

{ "status": "done" }


Ответ 200: объект задачи со статусом done.

4.5 Удалить задачу
URL: DELETE /api/tasks/10/
Headers: Authorization: Bearer <manager_or_admin_access>
Ответ 204: без тела.



5) Спец-эндпоинты (бизнес-логика)
5.1 Занятые сотрудники
URL: GET /api/tasks/busy-employees/
Headers: Authorization: Bearer <access>
Что делает: считает активные задачи (status = in_progress) у каждого сотрудника и сортирует по убыванию.
Ответ 200 (пример):

[
  {
    "employee": "Иванов Иван",
    "position": "Разработчик",
    "active_tasks_count": 2,
    "tasks": [
      { "id": 11, "title": "Модуль X", "status": "in_progress" },
      { "id": 12, "title": "Модуль Y", "status": "in_progress" }
    ]
  },
  {
    "employee": "Петров Пётр",
    "position": "Аналитик",
    "active_tasks_count": 0,
    "tasks": []
  }
]

5.2 Важные задачи
URL: GET /api/tasks/important-tasks/
Headers: Authorization: Bearer <access>
Что делает: берёт задачи не in_progress, у которых есть дочерние задачи в работе; предлагает кандидатов-исполнителей:

минимально загруженный сотрудник,

и/или исполнитель родительской задачи, если у него активных задач ≤ (минимум + 2).

Ответ 200 (пример):

[
  {
    "important_task": "Согласование ТЗ",
    "due_date": "2025-09-25",
    "candidates": ["Петров Пётр", "Иванов Иван"]
  },
  {
    "important_task": "Настройка CI",
    "due_date": null,
    "candidates": ["Петров Пётр"]
  }
]

Частые ошибки и решения
401 Unauthorized → нет/протух access:
Получи новый через /api/auth/token/ (логин) или обнови /api/auth/token/refresh/.
403 Forbidden → недостаточно прав (например, User пробует менять задачи).
Нужна роль manager или admin.
400 Bad Request → неверные поля/значения (например, status не из списка).
404 Not Found → объект не найден или скрыт политикой доступа.



Name                                  Stmts   Miss  Cover
---------------------------------------------------------
accounts\__init__.py                      0      0   100%
accounts\admin.py                         1      0   100%
accounts\apps.py                          4      0   100%
accounts\migrations\0001_initial.py       8      0   100%
accounts\migrations\__init__.py           0      0   100%
accounts\models.py                       12      0   100%
accounts\permissions.py                  13      1    92%
accounts\serializers.py                  50     10    80%
accounts\tests.py                        40      0   100%
accounts\urls.py                          7      0   100%
accounts\views.py                        32      1    97%
manage.py                                11      2    82%
tasktracker\__init__.py                   0      0   100%
tasktracker\settings.py                  27      0   100%
tasktracker\urls.py                       3      0   100%
tracker\__init__.py                       0      0   100%
tracker\admin.py                          1      0   100%
tracker\apps.py                           4      0   100%
tracker\migrations\0001_initial.py        6      0   100%
tracker\migrations\__init__.py            0      0   100%
tracker\models.py                        20      2    90%
tracker\permissions.py                   10      1    90%
tracker\serializers.py                   13      0   100%
tracker\tests.py                         65      0   100%
tracker\urls.py                           7      0   100%
tracker\views.py                         46      1    98%
---------------------------------------------------------
TOTAL                                   380     18    95%