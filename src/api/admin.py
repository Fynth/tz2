from django.contrib import admin

from .models import Category, Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "completed", "due_date", "created_at")
    list_filter = ("completed", "due_date", "created_at", "user")
    search_fields = ("id", "title", "description")
    readonly_fields = ("id", "created_at", "updated_at")
    filter_horizontal = ("categories",)

    fieldsets = (
        (None, {"fields": ("id", "title", "description", "user")}),
        ("Status", {"fields": ("completed",)}),
        ("Dates", {"fields": ("due_date", "created_at", "updated_at")}),
        ("Categories", {"fields": ("categories",)}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("id", "name", "description")
    readonly_fields = ("id", "created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("id", "name", "description")}),
        (
            "Dates",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
