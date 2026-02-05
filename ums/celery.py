import os

from celery import Celery

# Définir le module de configuration Django par défaut pour le programme 'celery'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ums.settings")

app = Celery("ums")

# Utiliser une chaîne ici signifie que le worker n'a pas besoin de sérialiser
# l'objet de configuration aux processus enfants.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Charger les modules de tâches de toutes les applications Django enregistrées
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
