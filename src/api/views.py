import logging

from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Category, Task
from .serializers import CategorySerializer, TaskSerializer

logger = logging.getLogger(__name__)


class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Filter tasks by the current user
        if self.request.user.is_authenticated:
            return Task.objects.filter(user=self.request.user)
        else:
            # For demo purposes, return tasks for the first user
            user = User.objects.first()
            if user:
                return Task.objects.filter(user=user)
            return Task.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            # For demo purposes, use or create the first user
            user = User.objects.first()
            if not user:
                user = User.objects.create_user(username="demo", password="demo")
            serializer.save(user=user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    lookup_field = "id"

    def get_queryset(self):
        # Ensure users can only access their own tasks
        if self.request.user.is_authenticated:
            return Task.objects.filter(user=self.request.user)
        else:
            # For demo purposes, return tasks for the first user
            user = User.objects.first()
            if user:
                return Task.objects.filter(user=user)
            return Task.objects.none()


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "id"


class UserTaskListView(generics.ListAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        # Get tasks for the currently authenticated user
        if self.request.user.is_authenticated:
            return Task.objects.filter(user=self.request.user)
        else:
            # For demo purposes, return tasks for the first user
            user = User.objects.first()
            if user:
                return Task.objects.filter(user=user)
            return Task.objects.none()


def get_user_by_telegram_id(request, telegram_id):
    """
    Helper endpoint for the bot to get user tasks by telegram ID
    In a real app, you would link telegram IDs to Django users
    """
    # For demo purposes, return tasks for the first user
    # In real implementation, you'd store telegram IDs with Django users
    user = User.objects.first()  # Default to first user for demo
    if user:
        tasks = Task.objects.filter(user=user)
        serializer = TaskSerializer(tasks, many=True)
        return JsonResponse(serializer.data, safe=False)
    return JsonResponse([], safe=False)
