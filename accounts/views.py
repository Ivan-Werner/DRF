from rest_framework import generics, permissions, viewsets
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer, UserWriteSerializer
from .permissions import IsAdmin, IsSelfOrAdmin

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """ Регистрация нового пользователя (всегда обычный user) """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveAPIView):
    """ Текущий пользователь (/me/) """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserViewSet(viewsets.ModelViewSet):
    """ CRUD пользователей """
    queryset = User.objects.all()

    def get_permissions(self):
        if self.action in ("list", "create", "destroy"):
            permission_classes = [permissions.IsAuthenticated, IsAdmin]
        elif self.action in ("retrieve", "update", "partial_update"):
            permission_classes = [permissions.IsAuthenticated, IsSelfOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [p() for p in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "is_admin", lambda: False)() or user.is_superuser:
            return User.objects.all().order_by("id")
        return User.objects.filter(id=user.id)

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return UserWriteSerializer
        return UserSerializer
