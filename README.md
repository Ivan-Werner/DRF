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

- **Тесты**: покрытие > 75% (~90%).

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