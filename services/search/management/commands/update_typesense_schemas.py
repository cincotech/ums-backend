import logging
import time

from django.core.management.base import BaseCommand

from services.search.client import TypesenseClient
from services.search.schemas import COLLECTION_SCHEMAS, MODEL_TO_COLLECTION

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Met à jour les schémas Typesense sans perte de données (ajout de champs)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--list",
            action="store_true",
            help="Liste les collections existantes et leurs champs",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Affiche les différences sans appliquer les modifications",
        )
        parser.add_argument(
            "--collection",
            type=str,
            nargs="+",
            help="Collections spécifiques à mettre à jour (par défaut toutes)",
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
            self._list_collections(client)
            return

        dry_run = options.get("dry_run", False)
        specific_collections = options.get("collection")

        self._update_schemas(client, dry_run=dry_run, only=specific_collections)

    def _list_collections(self, client):
        collections = client.list_collections()
        if not collections:
            self.stdout.write("Aucune collection trouvée.")
            return

        self.stdout.write(f"\n{len(collections)} collection(s) trouvée(s):")
        for coll in collections:
            fields = coll.get("fields", [])
            self.stdout.write(
                f"\n  {coll['name']} ({coll.get('num_documents', 0)} documents):"
            )
            for field in fields:
                optional = "(opt)" if field.get("optional") else ""
                ftype = field.get("type", "?")
                self.stdout.write(f"    - {field['name']}: {ftype} {optional}")

    def _update_schemas(self, client, dry_run=False, only=None):
        existing_collections = {c["name"]: c for c in client.list_collections()}

        for name, desired_schema in COLLECTION_SCHEMAS.items():
            if only and name not in only:
                continue

            if name not in existing_collections:
                self.stdout.write(f"\nNouvelle collection '{name}' — création...")
                if not dry_run:
                    success = client.create_collection(name, desired_schema)
                    if success:
                        self.stdout.write(
                            self.style.SUCCESS(f"  Collection '{name}' créée")
                        )
                    else:
                        self.stderr.write(f"  Échec de création de '{name}'")
                else:
                    self.stdout.write(f"  [DRY-RUN] Créerait la collection '{name}'")
                continue

            existing = existing_collections[name]
            existing_fields = {f["name"]: f for f in existing.get("fields", [])}
            desired_fields = {f["name"]: f for f in desired_schema.get("fields", [])}

            # Le champ 'id' est implicite dans Typesense, on ne peut pas
            # l'ajouter via l'API fields. On l'exclut de la comparaison.
            existing_fields.pop("id", None)
            desired_fields.pop("id", None)

            missing = {
                fn: fd for fn, fd in desired_fields.items() if fn not in existing_fields
            }

            if not missing:
                self.stdout.write(f"\n  '{name}' — déjà à jour")
                continue

            self.stdout.write(f"\n  '{name}' — {len(missing)} champ(s) manquant(s):")
            for fn, fd in missing.items():
                self.stdout.write(
                    f"    + {fn}: {fd['type']} (optional={fd.get('optional', False)})"
                )

            if dry_run:
                continue

            if not dry_run:
                try:
                    client._ensure_client()
                    client._client.collections[name].update(
                        {"fields": list(missing.values())}
                    )
                    for fn in missing:
                        self.stdout.write(f"    Ajouté: {fn}")
                    time.sleep(0.2)
                except Exception as e:
                    self.stderr.write(f"    Erreur lors de l'ajout des champs: {e}")

        if only:
            for name in only:
                if (
                    name not in MODEL_TO_COLLECTION.values()
                    and name not in COLLECTION_SCHEMAS
                ):
                    self.stdout.write(
                        f"\n  '{name}' — collection inconnue dans le schéma, ignorée"
                    )
