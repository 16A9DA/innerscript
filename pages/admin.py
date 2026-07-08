from django.contrib import admin

from .models import Toolkit


@admin.register(Toolkit)
class ToolkitAdmin(admin.ModelAdmin):
    list_display = ("title", "topic", "created")
    search_fields = ("title", "description")
