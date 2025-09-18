from django.contrib import admin

from tracker.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'parent', 'executor', 'due_date', 'status')
