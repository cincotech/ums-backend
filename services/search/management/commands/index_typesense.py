import logging
import time
from typing import Any

import typesense
from django.apps import apps
from django.core.management.base import BaseCommand, CommandParser

from services.search.client import TypesenseClient
from services.search.schemas import COLLECTION_SCHEMAS
from services.search.sync import DocumentSyncer

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Indexe (ou ré-indexe) tous les documents dans Typesense"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--models",
            nargs="+",
            choices=[
                "Course",
                "Module",
                "Teacher",
                "Class",
                "ClassGroup",
                "Department",
                "Faculty",
                "University",
                "User",
                "Inscription",
                "Student",
            ],
            help="Modèles à indexer (par défaut tous)",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Taille des lots pour l'import (défaut: 100)",
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=0.05,
            help="Délai entre chaque document en secondes (défaut: 0.05s)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Supprime la collection avant de réindexer",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Affiche des logs détaillés",
        )

    def handle(self, *args, **options) -> None:
        models = options.get("models") or [
            "Course",
            "Module",
            "Teacher",
            "Class",
            "ClassGroup",
            "Department",
            "Faculty",
            "University",
            "User",
            "Inscription",
            "Student",
        ]
        batch_size = options["batch_size"]
        delay = options["delay"]
        clear = options["clear"]
        verbose = options.get("verbose", False)

        self.stdout.write("=" * 60)
        self.stdout.write("🔍 INDEXATION TYPESENSE")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Modèles: {', '.join(models)}")
        self.stdout.write(f"Taille des lots: {batch_size}")
        self.stdout.write(f"Délai: {delay}s")
        self.stdout.write(f"Réinitialisation: {'Oui' if clear else 'Non'}")
        self.stdout.write("")

        client = TypesenseClient()
        syncer = DocumentSyncer()

        if not client.enabled:
            self.stderr.write(
                "❌ Typesense est désactivé. Vérifiez TYPESENSE_ENABLED et TYPESENSE_API_KEY."
            )
            return

        # Vérifier la connexion
        try:
            health = client.health_check()
            if health.get("status") != "ok":
                self.stderr.write(
                    f"❌ Typesense n'est pas disponible: {health.get('details', 'Unknown error')}"
                )
                return
            self.stdout.write(self.style.SUCCESS("✅ Connexion à Typesense établie"))
        except typesense.exceptions.TypesenseClientError as e:
            self.stderr.write(f"❌ Erreur de connexion: {e}")
            return

        total_indexed = 0
        total_errors = 0

        # Mapping model name -> app label
        model_app_map = {
            "Course": "course_app",
            "Module": "module_app",
            "Teacher": "teacher_app",
            "Class": "class_app",
            "ClassGroup": "class_app",
            "Department": "department_app",
            "Faculty": "faculty_app",
            "University": "university_app",
            "User": "user_app",
            "Inscription": "inscription_app",
            "Student": "student_profile_app",
        }

        for model_name in models:
            try:
                app_label = model_app_map.get(model_name)
                if not app_label:
                    self.stderr.write(f"❌ Modèle {model_name} non configuré.")
                    continue
                model = apps.get_model(app_label, model_name)
                queryset = model.objects.all()
                count = queryset.count()

                if count == 0:
                    self.stdout.write(f"⚠️ {model_name}: aucun document à indexer")
                    continue

                self.stdout.write(f"\n📦 {model_name} ({count} documents)")

                # Supprimer la collection si demandé
                collection_name = syncer._get_collection(model)
                if clear:
                    try:
                        client.delete_collection(collection_name)
                        self.stdout.write(f"  Collection '{collection_name}' supprimée")
                        # Attendre un peu pour la propagation
                        time.sleep(1)
                        # Recréer la collection avec le schéma approprié
                        schema = self._get_collection_schema(collection_name)
                        if schema:
                            client.create_collection(collection_name, schema)
                            self.stdout.write(
                                f"  Collection '{collection_name}' recréée"
                            )
                            time.sleep(0.5)
                    except typesense.exceptions.TypesenseClientError as e:
                        self.stderr.write(
                            f"  ⚠️ Erreur lors de la suppression de la collection: {e}"
                        )
                        continue

                # Vérifier/créer la collection
                # Note: la création des collections se fait via un script séparé pour plus de contrôle.

                # Indexation par lots

                # Indexation par lots
                indexed = 0
                errors = 0
                start_time = time.time()

                for i in range(0, count, batch_size):
                    batch = queryset[i : i + batch_size]
                    for instance in batch:
                        try:
                            syncer.index_instance(instance)
                            indexed += 1
                            if verbose and indexed % 50 == 0:
                                self.stdout.write(
                                    f"  {indexed}/{count} documents indexés",
                                    ending="\r",
                                )
                        except typesense.exceptions.TypesenseClientError as e:
                            errors += 1
                            self.stderr.write(
                                f"\n  ❌ Erreur sur {model_name} {instance.id}: {e}"
                            )
                            if verbose:
                                import traceback

                                traceback.print_exc()

                        # Petit délai pour éviter de surcharger Typesense
                        time.sleep(delay)

                    # Progression
                    self.stdout.write(
                        f"  {min(i+batch_size, count)}/{count} documents traités"
                    )

                elapsed = time.time() - start_time
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✅ {model_name}: {indexed} documents indexés, {errors} erreurs en {elapsed:.2f}s"
                    )
                )

                total_indexed += indexed
                total_errors += errors

            except LookupError:
                self.stderr.write(f"❌ Modèle {model_name} introuvable.")
            except typesense.exceptions.TypesenseClientError as e:
                self.stderr.write(
                    f"❌ Erreur lors de l'indexation de {model_name}: {e}"
                )
                if verbose:
                    import traceback

                    traceback.print_exc()
                total_errors += 1

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Indexation terminée: {total_indexed} documents indexés, {total_errors} erreurs"
            )
        )
        self.stdout.write("=" * 60)

    def _get_collection_schema(self, collection_name: str) -> dict[str, Any] | None:
        """Retourne le schéma autoritaire pour une collection donnée."""
        # Source unique : services/search/schemas.py (COLLECTION_SCHEMAS).
        # Tous les champs sauf id sont optionnels pour tolérer les attributs
        # absents ; created_at sert de default_sorting_field.
        return COLLECTION_SCHEMAS.get(collection_name)
