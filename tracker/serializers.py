from rest_framework import serializers
from .models import Employee, Task

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'position']


class TaskSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), allow_null=True, required=False)
    executor = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), allow_null=True, required=False)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'parent', 'executor', 'due_date', 'status', 'status_display']
