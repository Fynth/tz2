from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Category, Task


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class TaskSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.ListField(
        write_only=True, child=serializers.CharField(), required=False
    )

    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ["id", "user"]

    def create(self, validated_data, **kwargs):
        print(f"validated_data: {validated_data}")
        print(f"kwargs: {kwargs}")
        category_ids = validated_data.pop("category_ids", [])
        user = kwargs.get("user")
        if user:
            validated_data["user"] = user
        task = Task.objects.create(**validated_data)

        if category_ids:
            categories = Category.objects.filter(id__in=category_ids)
            task.categories.set(categories)

        return task

    def update(self, instance, validated_data):
        category_ids = validated_data.pop("category_ids", None)

        # Update all other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update categories if provided
        if category_ids is not None:
            categories = Category.objects.filter(id__in=category_ids)
            instance.categories.set(categories)

        return instance
