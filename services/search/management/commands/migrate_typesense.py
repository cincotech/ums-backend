import logging
import time

from django.apps import apps
from django.core.management.base import BaseCommand

from services.search.client import TypesenseClient
from services.search.schemas import COLLECTION_SCHEMAS, MODEL_TO_COLLECTION

logger = logging.getLogger(__name__)

INDEXED_MODEL_LABELS = [
    ("course_app", "Course"),
    ("module_app", "Module"),
    ("teacher_app", "Teacher"),
    ("class_app", "Class"),
    ("class_app", "ClassGroup"),
    ("department_app", "Department"),
    ("faculty_app", "Faculty"),
    ("university_app", "University"),
    ("user_app", "User"),
    ("inscription_app", "Inscription"),
    ("student_profile_app", "Student"),
]

COLLECTION_TO_MODEL = {v: k for k, v in MODEL_TO_COLLECTION.items()}


class Command(BaseCommand):
    help = (
        "Migration Typesense : crée/met à jour les schémas et indexe "
        "automatiquement les données manquantes"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--list",
            action="store_true",
            help="Liste les collections et leur état sans rien modifier",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simule les opérations sans les appliquer",
        )
        parser.add_argument(
            "--collection",
            type=str,
            nargs="+",
            help="Collections spécifiques à traiter (par défaut toutes)",
        )

    def handle(self, *args, **options):
        client = TypesenseClient()

        if not client.enabled:
            self.stderr.write("Typesense est désactivé.")
            return

        health = client.health_check()
        if health.get("status") != "ok":
            self.stderr.write(
                f"Typesense n'est pas disponible: {health.get('details')}"
            )
            return

        self.stdout.write(self.style.SUCCESS("Connexion à Typesense établie"))

        if options.get("list"):
            self._report(client)
            return

        dry_run = options.get("dry_run", False)
        only = options.get("collection")

        self._migrate(client, dry_run=dry_run, only=only)

    def _report(self, client):
        existing = {c["name"]: c for c in client.list_collections()}
        self.stdout.write("\n=== État des collections Typesense ===\n")

        for name, schema in COLLECTION_SCHEMAS.items():
            if name in existing:
                coll = existing[name]
                doc_count = coll.get("num_documents", 0)
                existing_fields = {f["name"] for f in coll.get("fields", [])}
                desired_fields = {f["name"] for f in schema.get("fields", [])}
                # 'id' est implicite dans Typesense
                existing_fields.discard("id")
                desired_fields.discard("id")
                missing = desired_fields - existing_fields
                extra = existing_fields - desired_fields
                status = "À JOUR"
                if missing:
                    status = f"{len(missing)} CHAMP(S) MANQUANT(S)"
                self.stdout.write(f"  {name:20s} {doc_count:>6} docs  {status}")
                if missing:
                    for fn in sorted(missing):
                        self.stdout.write(f"    + {fn}")
                if extra:
                    for fn in sorted(extra):
                        self.stdout.write(f"    - {fn} (hors schéma)")
            else:
                self.stdout.write(f"  {name:20s} {'-':>6}      MANQUANTE")

        self.stdout.write("")

    def _migrate(self, client, dry_run=False, only: set[str] | None = None):
        existing = {c["name"]: c for c in client.list_collections()}

        pending_index: dict[str, bool] = {}
        total_created = 0
        total_updated = 0
        total_indexed = 0
        total_errors = 0

        for name, desired_schema in COLLECTION_SCHEMAS.items():
            if only and name not in only:
                continue

            self.stdout.write(f"\n▶ {name}")

            # Phase 1 : créer la collection si elle n'existe pas
            if name not in existing:
                self.stdout.write("  Création de la collection...")
                if not dry_run:
                    success = client.create_collection(name, desired_schema)
                    if success:
                        self.stdout.write(self.style.SUCCESS("  ✅ Collection créée"))
                        total_created += 1
                        pending_index[name] = True
                        time.sleep(0.5)
                    else:
                        self.stderr.write("  ❌ Échec de création")
                        total_errors += 1
                        continue
                else:
                    self.stdout.write("  [DRY-RUN] Collection à créer")
                    pending_index[name] = True
                    continue
            else:
                coll = existing[name]
                existing_fields = {f["name"]: f for f in coll.get("fields", [])}
                desired_fields = {
                    f["name"]: f for f in desired_schema.get("fields", [])
                }

                # Le champ 'id' est implicite dans Typesense — on ne peut
                # pas l'ajouter via l'API fields.
                existing_fields.pop("id", None)
                desired_fields.pop("id", None)

                missing = {
                    fn: fd
                    for fn, fd in desired_fields.items()
                    if fn not in existing_fields
                }

                if missing:
                    self.stdout.write(
                        f"  Mise à jour : {len(missing)} champ(s) manquant(s)"
                    )
                    for fn, fd in missing.items():
                        self.stdout.write(f"    + {fn}: {fd['type']}")
                    if not dry_run:
                        try:
                            client._ensure_client()
                            client._client.collections[name].update(
                                {"fields": list(missing.values())}
                            )
                            total_updated += 1
                            time.sleep(0.3)
                        except Exception as e:
                            self.stderr.write(
                                f"    ❌ Erreur mise à jour '{name}': {e}"
                            )
                            total_errors += 1
                else:
                    self.stdout.write("  Schéma à jour")

            # Phase 2 : décider s'il faut indexer
            if name not in pending_index:
                if name in existing:
                    doc_count = existing[name].get("num_documents", 0)
                    if doc_count == 0:
                        pending_index[name] = True
                        self.stdout.write("  Collection vide — indexation nécessaire")
                    else:
                        self.stdout.write(f"  {doc_count} document(s) déjà présent(s)")
                        pending_index[name] = False
                else:
                    pending_index[name] = True

        # Phase 3 : indexer les données
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("PHASE D'INDEXATION")
        self.stdout.write("=" * 60)

        for name, should_index in pending_index.items():
            if not should_index:
                continue
            if only and name not in only:
                continue

            model_name = COLLECTION_TO_MODEL.get(name)
            if not model_name:
                self.stdout.write(f"\n  {name}: aucun modèle Django associé, ignoré")
                continue

            app_label = None
            for al, mn in INDEXED_MODEL_LABELS:
                if mn == model_name:
                    app_label = al
                    break

            if not app_label:
                self.stdout.write(
                    f"\n  {name}: modèle '{model_name}' non trouvé dans INDEXED_MODEL_LABELS"
                )
                continue

            if dry_run:
                self.stdout.write(f"\n  {name}: [DRY-RUN] indexerait {model_name}")
                continue

            try:
                model = apps.get_model(app_label, model_name)
                queryset = model.objects.all()
                total = queryset.count()

                if total == 0:
                    self.stdout.write(f"\n  {name}: aucun {model_name} à indexer")
                    continue

                self.stdout.write(f"\n  {name} ({model_name}) : {total} document(s)")
                from services.search.sync import syncer

                batch_size = 100
                indexed = 0
                errors = 0

                for i in range(0, total, batch_size):
                    batch = queryset[i : i + batch_size]
                    for instance in batch:
                        try:
                            syncer.index_instance(instance)
                            indexed += 1
                        except Exception as e:
                            errors += 1
                            self.stderr.write(f"    ❌ {model_name} {instance.id}: {e}")
                    self.stdout.write(
                        f"    {min(i + batch_size, total)}/{total}", ending="\r"
                    )
                    time.sleep(0.05)

                if errors:
                    self.stdout.write(
                        self.style.WARNING(
                            f"\n  ✅ Indexé: {indexed}, Erreurs: {errors}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f"\n  ✅ {indexed} document(s) indexés")
                    )
                total_indexed += indexed
                total_errors += errors

            except LookupError:
                self.stderr.write(
                    f"\n  ❌ Modèle '{model_name}' introuvable dans '{app_label}'"
                )
                total_errors += 1

        # Résumé final
        self.stdout.write("\n" + "=" * 60)
        msg_parts = []
        if total_created:
            msg_parts.append(f"{total_created} collection(s) créée(s)")
        if total_updated:
            msg_parts.append(f"{total_updated} collection(s) mise(s) à jour")
        if total_indexed:
            msg_parts.append(f"{total_indexed} document(s) indexé(s)")
        if total_errors:
            msg_parts.append(f"{total_errors} erreur(s)")
        if not msg_parts:
            msg_parts.append("Rien à faire — tout est à jour")

        if dry_run:
            self.stdout.write(f"[DRY-RUN] {' | '.join(msg_parts)}")
        elif total_errors and not total_indexed and not total_created:
            self.stderr.write(f"ÉCHEC — {' | '.join(msg_parts)}")
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ {' | '.join(msg_parts)}"))
        self.stdout.write("=" * 60)
