from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """
    Доступ только для админов (роль admin или суперпользователь).
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (getattr(user, "is_admin", lambda: False)() or user.is_superuser)
        )


class IsSelfOrAdmin(BasePermission):
    """
    Пользователь может работать только со своим объектом;
    Админ — с любым.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, "is_admin", lambda: False)() or user.is_superuser:
            return True
        return obj.id == user.id
