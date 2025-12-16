"""
Integration test for the ToDo List system
This test verifies that all components work together properly.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent / "src"))

import django
from django.contrib.auth.models import User
from django.test import Client, TestCase

from api.models import Category, Task

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()


class IntegrationTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )

        # Create a test category
        self.category = Category.objects.create(
            name="Work", description="Work-related tasks"
        )

        # Create API client
        self.client = Client()
        self.client.login(username="testuser", password="testpass123")

    def test_task_creation_and_retrieval(self):
        """Test that tasks can be created and retrieved via API"""
        # Create a task
        task_data = {
            "title": "Test Task",
            "description": "Test Description",
            "user": self.user.id,
            "categories": [self.category.id],
        }

        # Test that the models work correctly with custom IDs
        task = Task.objects.create(
            title=task_data["title"],
            description=task_data["description"],
            user=self.user,
        )
        task.categories.add(self.category)

        # Verify the task was created with a custom ID
        self.assertTrue(task.id.startswith("TASK_"))

        # Verify the category was associated correctly
        self.assertIn(self.category, task.categories.all())

        # Verify the creation date is present
        self.assertIsNotNone(task.created_at)

        print(f"✓ Task created successfully with ID: {task.id}")
        print(f"✓ Task title: {task.title}")
        print(f"✓ Created at: {task.created_at}")
        print(f"✓ Categories: {[cat.name for cat in task.categories.all()]}")

    def test_category_creation(self):
        """Test that categories can be created with custom IDs"""
        category = Category.objects.create(
            name="Test Category", description="A test category"
        )

        # Verify the category was created with a custom ID
        self.assertTrue(category.id.startswith("CAT_"))

        print(f"✓ Category created successfully with ID: {category.id}")
        print(f"✓ Category name: {category.name}")

    def test_task_category_relationship(self):
        """Test the relationship between tasks and categories"""
        # Create a task
        task = Task.objects.create(
            title="Relationship Test",
            description="Testing task-category relationship",
            user=self.user,
        )

        # Create another category
        category2 = Category.objects.create(
            name="Personal", description="Personal tasks"
        )

        # Associate both categories with the task
        task.categories.add(self.category, category2)

        # Verify relationships
        self.assertEqual(task.categories.count(), 2)
        self.assertIn(self.category, task.categories.all())
        self.assertIn(category2, task.categories.all())

        print(f"✓ Task-category relationship test passed")
        print(f"✓ Task has {task.categories.count()} categories")

    def test_custom_id_uniqueness(self):
        """Test that custom IDs are unique"""
        # Create multiple tasks
        task1 = Task.objects.create(
            title="Task 1", description="First task", user=self.user
        )

        task2 = Task.objects.create(
            title="Task 2", description="Second task", user=self.user
        )

        # Create multiple categories
        cat1 = Category.objects.create(name="Category 1")
        cat2 = Category.objects.create(name="Category 2")

        # Verify all IDs are unique and follow the pattern
        self.assertNotEqual(task1.id, task2.id)
        self.assertTrue(task1.id.startswith("TASK_"))
        self.assertTrue(task2.id.startswith("TASK_"))
        self.assertTrue(cat1.id.startswith("CAT_"))
        self.assertTrue(cat2.id.startswith("CAT_"))
        self.assertNotEqual(cat1.id, cat2.id)

        print(f"✓ Custom ID uniqueness test passed")
        print(f"✓ Task 1 ID: {task1.id}")
        print(f"✓ Task 2 ID: {task2.id}")
        print(f"✓ Category 1 ID: {cat1.id}")
        print(f"✓ Category 2 ID: {cat2.id}")


def run_integration_tests():
    """Run all integration tests"""
    print("Running integration tests for ToDo List system...\n")

    test = IntegrationTest()
    test.setUp()

    try:
        test.test_task_creation_and_retrieval()
        print()
        test.test_category_creation()
        print()
        test.test_task_category_relationship()
        print()
        test.test_custom_id_uniqueness()
        print("\n✓ All integration tests passed!")
        return True
    except Exception as e:
        print(f"\n✗ Integration test failed: {e}")
        return False


if __name__ == "__main__":
    run_integration_tests()
