import logging

from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Task


@shared_task
def check_due_tasks():
    """
    Check for tasks that are due and send notifications
    """
    now = timezone.now()
    due_tasks = Task.objects.filter(due_date__lte=now, completed=False)

    for task in due_tasks:
        logger.info(f"Task '{task.title}' is due for user {task.user.username}")
        # Send notification logic would go here
        # This could involve calling a notification service
        # or queuing a message to be sent via Telegram, email, etc.
        send_task_notification.delay(task.id)

    return f"Checked {len(due_tasks)} due tasks"


@shared_task
def send_task_notification(task_id):
    """
    Send notification for a specific task
    """
    try:
        task = Task.objects.get(id=task_id)
        # In a real implementation, this would send actual notifications
        # For now, we'll log the notification
        logger.info(
            f"Notification sent for task '{task.title}' to user {task.user.username}"
        )
        # For now, we'll log the notification
        logger.info(f"Notification sent for task '{task.title}' to user {task.user.username}")

        # Future enhancement: Send actual notification via Telegram, email, etc.
        return f"Notification sent for task {task.id}"
    except Task.DoesNotExist:
        logger.error(f"Task with id {task_id} does not exist")
        return f"Task with id {task_id} does not exist"
