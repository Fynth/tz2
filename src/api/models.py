from core.id_generator import generate_category_id, generate_task_id
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class CustomIDField(models.CharField):
    """
    Custom field for generating unique IDs without using UUID, random,
    or standard postgres functions.
    """

    def __init__(self, prefix="", *args, **kwargs):
        self.prefix = prefix
        kwargs.setdefault("max_length", 50)
        kwargs.setdefault("unique", True)
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        if add and not getattr(model_instance, self.attname):
            if hasattr(self, "prefix"):
                if self.prefix == "TASK":
                    value = generate_task_id()
                elif self.prefix == "CAT":
                    value = generate_category_id()
                else:
                    # Fallback for other prefixes
                    value = generate_task_id()  # Or implement generic generator
            else:
                # If no prefix is set, use task as default
                value = generate_task_id()

            setattr(model_instance, self.attname, value)
            return value
        return super().pre_save(model_instance, add)


class Category(models.Model):
    id = CustomIDField(prefix="CAT", primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]


class Task(models.Model):
    id = CustomIDField(prefix="TASK", primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Date of creation as required
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    categories = models.ManyToManyField(Category, blank=True, related_name="tasks")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]
