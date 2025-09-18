from django.db.models import Count, Q
from rest_framework import viewsets, permissions, decorators, response
from .models import Employee, Task
from .serializers import EmployeeSerializer, TaskSerializer
from .permissions import IsManagerOrAdminForUnsafe
from rest_framework import status


ACTIVE_Q = Q(tasks__status=Task.Status.IN_PROGRESS)

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiExample,
    OpenApiParameter,
)


@extend_schema_view(
    list=extend_schema(
        summary="Список сотрудников",
        tags=["Employees"],
    ),
    retrieve=extend_schema(
        summary="Получить сотрудника",
        tags=["Employees"],
    ),
    create=extend_schema(
        summary="Создать сотрудника",
        tags=["Employees"],
        examples=[
            OpenApiExample(
                "Пример",
                value={"full_name": "Иванов Иван", "position": "Разработчик"},
                request_only=True,
            )
        ],
    ),
    partial_update=extend_schema(summary="Изменить сотрудника", tags=["Employees"]),
    destroy=extend_schema(summary="Удалить сотрудника", tags=["Employees"]),
)
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by("id")
    serializer_class = EmployeeSerializer
    permission_classes = [
        IsManagerOrAdminForUnsafe
    ]  # менеджер/админ — изменяют; все auth — читают


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related("executor", "parent").all().order_by("id")
    serializer_class = TaskSerializer
    permission_classes = [
        IsManagerOrAdminForUnsafe
    ]  # менеджер/админ — изменяют; все auth — читают

    @decorators.action(
        detail=False,
        methods=["get"],
        url_path="busy-employees",
        permission_classes=[permissions.IsAuthenticated],
    )
    def busy_employees(self, request):
        """
        Список сотрудников с их активными задачами, отсортированный по количеству активных задач (desc).
        Активная = status = in_progress.
        """
        qs = Employee.objects.annotate(
            active_tasks_count=Count(
                "tasks", filter=Q(tasks__status=Task.Status.IN_PROGRESS)
            )
        ).order_by("-active_tasks_count", "id")

        active_tasks = Task.objects.filter(
            status=Task.Status.IN_PROGRESS, executor__in=qs
        ).select_related("executor")
        tasks_by_emp = {}
        for t in active_tasks:
            tasks_by_emp.setdefault(t.executor_id, []).append(
                {
                    "id": t.id,
                    "title": t.title,
                    "status": t.status,
                }
            )

        data = []
        for emp in qs:
            data.append(
                {
                    "employee": emp.full_name,
                    "position": emp.position,
                    "active_tasks_count": emp.active_tasks_count,
                    "tasks": tasks_by_emp.get(emp.id, []),
                }
            )
        return response.Response(data)

    @decorators.action(
        detail=False,
        methods=["get"],
        url_path="important-tasks",
        permission_classes=[permissions.IsAuthenticated],
    )
    def important_tasks(self, request):
        """
        Важные задачи:
        - задача НЕ в работе (не in_progress),
        - но от неё зависят задачи (children), которые уже в работе.

        Кандидаты:
        - наименее загруженный сотрудник (минимум активных задач),
        - И/ИЛИ исполнитель родительской задачи, если у него <= (min + 2) активных.
        """
        employees = Employee.objects.annotate(
            active_count=Count("tasks", filter=Q(tasks__status=Task.Status.IN_PROGRESS))
        ).order_by("active_count", "id")
        if not employees.exists():
            return response.Response([])

        least_loaded = employees.first()
        least_count = least_loaded.active_count or 0
        threshold = least_count + 2

        important = (
            Task.objects.filter(~Q(status=Task.Status.IN_PROGRESS))
            .filter(children__status=Task.Status.IN_PROGRESS)
            .select_related("parent", "executor")
            .distinct()
            .order_by("due_date", "id")
        )

        load_map = {e.id: (e.active_count or 0) for e in employees}

        result = []
        for t in important:
            candidates = set()
            candidates.add(least_loaded.full_name)

            if t.executor_id:
                parent_exec = t.executor
                parent_load = load_map.get(parent_exec.id, 0)
                if parent_load <= threshold:
                    candidates.add(parent_exec.full_name)

            result.append(
                {
                    "important_task": t.title,
                    "due_date": t.due_date,
                    "candidates": sorted(list(candidates)),
                }
            )

        return response.Response(result)
