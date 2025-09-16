from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from tracker.models import Employee, Task

User = get_user_model()


class TrackerAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            password="Admin123!@#",
            role=User.Roles.ADMIN,
            is_superuser=True,
            is_staff=True,
        )
        self.manager = User.objects.create_user(
            username="manager", password="Manager123!@#", role=User.Roles.MANAGER
        )
        self.user = User.objects.create_user(
            username="user", password="User123!@#", role=User.Roles.USER
        )

        self.emp1 = Employee.objects.create(
            full_name="Иванов Иван", position="Разработчик"
        )
        self.emp2 = Employee.objects.create(
            full_name="Петров Пётр", position="Аналитик"
        )
        self.emp3 = Employee.objects.create(
            full_name="Сидоров Сидор", position="Тестировщик"
        )

        self.client = APIClient()

    # ---------- Employees CRUD ----------

    def test_user_cannot_create_employee_manager_can(self):
        # обычный юзер: 403
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(
            "/api/employees/",
            {"full_name": "Новый Сотр", "position": "Стажёр"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # менеджер: 201
        self.client.force_authenticate(user=self.manager)
        resp = self.client.post(
            "/api/employees/",
            {"full_name": "Новый Сотр", "position": "Стажёр"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    # ---------- Tasks CRUD ----------

    def test_user_cannot_create_task_manager_can(self):
        task_payload = {
            "title": "Подготовить отчёт",
            "description": "Собрать статусы",
            "parent": None,
            "executor": self.emp1.id,
            "due_date": "2025-09-22",
            "status": Task.Status.NEW,
        }
        # user: 403
        self.client.force_authenticate(user=self.user)
        resp = self.client.post("/api/tasks/", task_payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # manager: 201
        self.client.force_authenticate(user=self.manager)
        resp = self.client.post("/api/tasks/", task_payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_manager_can_update_task_status(self):
        self.client.force_authenticate(user=self.manager)
        t = Task.objects.create(
            title="Задача", executor=self.emp1, status=Task.Status.NEW
        )
        resp = self.client.patch(
            f"/api/tasks/{t.id}/", {"status": Task.Status.IN_PROGRESS}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["status"], Task.Status.IN_PROGRESS)

    # ---------- busy-employees ----------

    def test_busy_employees_counts_and_ordering(self):
        # emp1: 2 активных, emp2: 1 активная, emp3: 0
        Task.objects.create(
            title="A1", executor=self.emp1, status=Task.Status.IN_PROGRESS
        )
        Task.objects.create(
            title="A2", executor=self.emp1, status=Task.Status.IN_PROGRESS
        )
        Task.objects.create(
            title="B1", executor=self.emp2, status=Task.Status.IN_PROGRESS
        )
        Task.objects.create(title="C1", executor=self.emp3, status=Task.Status.NEW)

        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/tasks/busy-employees/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        # порядок: emp1 (2), emp2 (1), emp3 (0)
        self.assertGreaterEqual(
            data[0]["active_tasks_count"], data[1]["active_tasks_count"]
        )
        self.assertGreaterEqual(
            data[1]["active_tasks_count"], data[2]["active_tasks_count"]
        )
        # проверим совпадение имён
        names = [d["employee"] for d in data]
        self.assertIn(self.emp1.full_name, names)
        self.assertIn(self.emp2.full_name, names)
        self.assertIn(self.emp3.full_name, names)

    # ---------- important-tasks ----------

    def test_important_tasks_candidates_selection(self):
        """
        Важная задача = НЕ in_progress, но от нее зависит задача в работе.
        Кандидаты:
          - минимально загруженный сотрудник
          - И/ИЛИ исполнитель важной задачи, если его нагрузка <= min + 2
        """
        # активные нагрузки:
        # emp1: 0 активных
        # emp2: 1 активная
        # emp3: 2 активных
        Task.objects.create(
            title="load2-1", executor=self.emp3, status=Task.Status.IN_PROGRESS
        )
        Task.objects.create(
            title="load2-2", executor=self.emp3, status=Task.Status.IN_PROGRESS
        )
        Task.objects.create(
            title="load1-1", executor=self.emp2, status=Task.Status.IN_PROGRESS
        )

        # важная задача (родитель), НЕ в работе, с исполнителем emp2
        important = Task.objects.create(
            title="ВАЖНАЯ", executor=self.emp2, status=Task.Status.NEW
        )

        # зависимая задача в работе (child -> in_progress)
        child = Task.objects.create(
            title="child in work",
            parent=important,
            executor=self.emp3,
            status=Task.Status.IN_PROGRESS,
        )

        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/tasks/important-tasks/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        items = resp.json()
        # должна быть найдена "ВАЖНАЯ"
        item = next((x for x in items if x["important_task"] == "ВАЖНАЯ"), None)
        self.assertIsNotNone(item)

        candidates = set(item["candidates"])
        # минимально загруженный = emp1 (0 активных)
        self.assertIn(self.emp1.full_name, candidates)

        # исполнитель важной задачи emp2 имеет 1 активную — порог 0+2=2, значит тоже подходит
        self.assertIn(self.emp2.full_name, candidates)
