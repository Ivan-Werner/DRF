from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'admin', 'Админ'
        MANAGER = 'manager', 'Менеджер'
        USER = 'user', 'Пользователь'

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.USER,
    )

    def is_admin(self):
        return self.role == self.Roles.ADMIN or self.is_superuser

    def is_manager(self):
        return self.role == self.Roles.MANAGER
