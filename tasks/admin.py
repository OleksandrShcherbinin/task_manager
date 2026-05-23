from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'due_date', 'is_done', 'created_at')
    list_filter = ('priority', 'is_done')
    search_fields = ('title', 'description')
