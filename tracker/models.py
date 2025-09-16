from django.db import models

class Employee(models.Model):
    full_name = models.CharField(max_length=255)
    position = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.full_name


class Task(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'Новая'
        IN_PROGRESS = 'in_progress', 'В работе'
        DONE = 'done', 'Готово'
        BLOCKED = 'blocked', 'Заблокирована'

    title = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True,
                               on_delete=models.SET_NULL,
                               related_name='children')
    executor = models.ForeignKey(Employee, null=True, blank=True,
                                 on_delete=models.SET_NULL,
                                 related_name='tasks')
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title
