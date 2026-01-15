from celery.schedules import crontab

# Configuration des tâches périodiques
CELERY_BEAT_SCHEDULE = {
    "send-payment-reminders": {
        "task": "dashboard_collection_agent_app.tasks.send_payment_reminders",
        "schedule": crontab(hour=9, minute=0),  # Tous les jours à 9h
    },
    "update-overdue-installments": {
        "task": "dashboard_collection_agent_app.tasks.update_overdue_installments",
        "schedule": crontab(hour=0, minute=30),  # Tous les jours à 00h30
    },
}
