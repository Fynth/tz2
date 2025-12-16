from api.tasks import check_due_tasks
from celery.schedules import crontab
from core.celery import app as celery_app

# Configure periodic task to check for due tasks every minute
celery_app.conf.beat_schedule = {
    "check-due-tasks": {
        "task": "api.tasks.check_due_tasks",
        "schedule": crontab(minute="*"),  # Run every minute
    },
}

celery_app.conf.timezone = "UTC"
