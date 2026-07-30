import logging
import time

from django.core.management.base import BaseCommand

from services.search.client import TypesenseClient
from services.search.schemas import COLLECTION_SCHEMAS

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Crée les collections Typesense avec les schémas appropriés"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Supprime les collections existantes avant de les recréer",
        )
        parser.add_argument(
            "--list",
            action="store_true",
            help="Liste les collections existantes sans en créer",
        )

    def handle(self, *args, **options):
        client = TypesenseClient()

        if not client.enabled:
            self.stderr.write("❌ Typesense est désactivé. Vérifiez la configuration.")
            return

        # Vérifier la connexion
        health = client.health_check()
        if health.get("status") != "ok":
            self.stderr.write(
                f"❌ Typesense n'est pas disponible: {health.get('details', 'Unknown error')}"
            )
            return

        self.stdout.write(self.style.SUCCESS("✅ Connexion à Typesense établie"))

        if options.get("list"):
            self._list_collections(client)
            return

        self._create_collections(client, force=options.get("force"))

    def _list_collections(self, client):
        """Liste les collections existantes."""
        collections = client.list_collections()
        if collections:
            self.stdout.write(f"\n📚 {len(collections)} collection(s) trouvée(s):")
            for coll in collections:
                self.stdout.write(
                    f"  - {coll['name']} ({coll.get('num_documents', 0)} documents)"
                )
        else:
            self.stdout.write("\n📭 Aucune collection trouvée.")

    def _create_collections(self, client, force=False):
        """Crée les collections avec leurs schémas."""
        # Schéma autoritaire unique (services/search/schemas.py).
        schemas = COLLECTION_SCHEMAS

        for name, schema in schemas.items():
            if force:
                self.stdout.write(f"🗑️  Suppression de la collection '{name}'...")
                client.delete_collection(name)
                time.sleep(0.5)

            self.stdout.write(f"📦 Création de la collection '{name}'...")
            success = client.create_collection(name, schema)
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ Collection '{name}' créée avec succès")
                )
            else:
                self.stderr.write(
                    f"  ❌ Échec de la création de la collection '{name}'"
                )

    def _get_schemas(self):
        """Retourne les schémas autoritaires (source unique dans schemas.py)."""
        return COLLECTION_SCHEMAS
