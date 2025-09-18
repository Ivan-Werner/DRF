from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["username", "password", "email", "first_name", "last_name", "role"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            role=User.Roles.USER,
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор для чтения.
    """

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role"]


class UserWriteSerializer(serializers.ModelSerializer):
    """
    Создание/обновление пользователей.
    - Пароль задается/меняется через отдельное поле password.
    - Поле role может править только админ.
    """

    password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "role", "password"]

    def validate(self, attrs):
        """Запрет изменения role не-админу"""
        request = self.context.get("request")
        is_admin = bool(
            request
            and request.user
            and (
                getattr(request.user, "is_admin", lambda: False)()
                or request.user.is_superuser
            )
        )

        if not is_admin and "role" in attrs:
            raise serializers.ValidationError(
                {"role": "Изменять роль может только администратор."}
            )
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            validate_password(password)
            user.set_password(password)
        else:
            raise serializers.ValidationError(
                {"password": "Пароль обязателен при создании пользователя."}
            )
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            validate_password(password)
            instance.set_password(password)
        instance.save()
        return instance
