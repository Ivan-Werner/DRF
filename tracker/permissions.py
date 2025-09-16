from rest_framework.permissions import BasePermission, SAFE_METHODS

def _is_admin(user):
    return bool(user and user.is_authenticated and (getattr(user, "is_admin", lambda: False)() or user.is_superuser))

def _is_manager(user):
    return bool(user and user.is_authenticated and getattr(user, "is_manager", lambda: False)())

class IsManagerOrAdminForUnsafe(BasePermission):
    """
    Разрешает любые SAFE-методы всем аутентифицированным,
    а небезопасные (POST/PUT/PATCH/DELETE) — только менеджеру/админу.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return _is_admin(request.user) or _is_manager(request.user)
