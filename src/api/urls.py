from django.urls import path

from . import views

urlpatterns = [
    # Task URLs
    path("tasks/", views.TaskListCreateView.as_view(), name="task-list-create"),
    path("tasks/<str:id>/", views.TaskDetailView.as_view(), name="task-detail"),
    path(
        "users/<str:username>/tasks/",
        views.UserTaskListView.as_view(),
        name="user-task-list",
    ),
    # Category URLs
    path(
        "categories/",
        views.CategoryListCreateView.as_view(),
        name="category-list-create",
    ),
    path(
        "categories/<str:id>/",
        views.CategoryDetailView.as_view(),
        name="category-detail",
    ),
    # Telegram bot integration
    path(
        "telegram/user/<int:telegram_id>/tasks/",
        views.get_user_by_telegram_id,
        name="telegram-user-tasks",
    ),
]
