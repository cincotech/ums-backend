"""
Management command to set up synonyms in Typesense using the v30+ synonym_sets API.

Usage:
    python manage.py setup_synonyms [--clear]

Typesense v30+ deprecates per-collection synonyms and replaces them with
global synonym_sets. Each collection references a synonym set via its
`synonym_sets` field in the collection schema.

This command:
1. Creates/updates the global "ums-synonyms" synonym set
2. Optionally updates each collection schema to reference the synonym set
"""

import logging

from django.core.management.base import BaseCommand, CommandParser

from services.search.client import TypesenseClient
from services.search.synonyms import UMS_SYNONYM_SET_NAME, build_typesense_synonym_items

logger = logging.getLogger(__name__)

# Collections that should use the UMS synonym set
MANAGED_COLLECTIONS = [
    "courses",
    "modules",
    "teachers",
    "classes",
    "departments",
    "faculties",
    "universities",
    "users",
]


class Command(BaseCommand):
    help = "Configure les synonymes Typesense v30+ (synonym_sets globaux)"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Supprime le synonym set existant avant de le recréer",
        )
        parser.add_argument(
            "--update-collections",
            action="store_true",
            help="Met à jour les schémas des collections pour référencer le synonym set",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Affiche ce qui serait fait sans appliquer",
        )

    def handle(self, *args, **options) -> None:
        clear = options.get("clear", False)
        update_collections = options.get("update_collections", False)
        dry_run = options.get("dry_run", False)

        self.stdout.write("=" * 60)
        self.stdout.write("📖 CONFIGURATION DES SYNONYMES TYPESENSE (v30+)")
        self.stdout.write("=" * 60)

        if dry_run:
            self.stdout.write("⚠️  DRY RUN — aucune modification ne sera appliquée")
        self.stdout.write(f"Synonym set: {UMS_SYNONYM_SET_NAME}")
        self.stdout.write("")

        client = TypesenseClient()

        if not client.enabled:
            self.stderr.write("❌ Typesense est désactivé.")
            return

        # Vérifier la connexion
        try:
            health = client.health_check()
            if health.get("status") != "ok":
                self.stderr.write(f"❌ Typesense n'est pas disponible: {health}")
                return
            self.stdout.write(self.style.SUCCESS("✅ Connexion à Typesense établie"))
        except Exception as e:
            self.stderr.write(f"❌ Erreur de connexion: {e}")
            return

        # Étape 1 : Créer/mettre à jour le synonym set global
        self._setup_synonym_set(client, clear, dry_run)

        # Étape 2 : Mettre à jour les collections pour référencer le synonym set
        if update_collections:
            self._update_collection_schemas(client, dry_run)
        else:
            self.stdout.write(
                "\n💡 Pour appliquer le synonym set aux collections, relance avec --update-collections"
            )

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("✅ Terminé"))
        self.stdout.write("=" * 60)

    # ------------------------------------------------------------------
    # Synonym set management
    # ------------------------------------------------------------------

    def _setup_synonym_set(
        self, client: TypesenseClient, clear: bool, dry_run: bool
    ) -> None:
        """Crée ou met à jour le synonym set global UMS."""
        items = build_typesense_synonym_items()
        self.stdout.write(f"\n📦 Préparation de {len(items)} groupes de synonymes...")

        if dry_run:
            self.stdout.write(
                f"   [DRY RUN] Synonym set '{UMS_SYNONYM_SET_NAME}' serait créé/mis à jour avec {len(items)} items"
            )
            for item in items[:5]:
                self.stdout.write(f"   - {item['id']}: {item['synonyms'][:3]}...")
            if len(items) > 5:
                self.stdout.write(f"   ... et {len(items) - 5} autres")
            return

        try:
            # Supprimer l'existant si demandé
            if clear:
                self._delete_synonym_set(client)

            # Upsert le synonym set
            result = client._client.synonym_sets[UMS_SYNONYM_SET_NAME].upsert(
                {"items": items}
            )
            item_count = len(result.get("items", []))
            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✅ Synonym set '{UMS_SYNONYM_SET_NAME}' configuré avec {item_count} items"
                )
            )

        except Exception as e:
            self.stderr.write(f"  ❌ Erreur lors de la création du synonym set: {e}")
            logger.exception("Échec de création du synonym set")

    def _delete_synonym_set(self, client: TypesenseClient) -> None:
        """Supprime le synonym set global s'il existe."""
        try:
            client._client.synonym_sets[UMS_SYNONYM_SET_NAME].delete()
            self.stdout.write(f"  🗑️  Synonym set '{UMS_SYNONYM_SET_NAME}' supprimé")
        except Exception as e:
            # 404 = le set n'existe pas, ce n'est pas une erreur
            if "404" not in str(e):
                self.stdout.write(f"  ⚠️ Échec suppression du synonym set: {e}")

    # ------------------------------------------------------------------
    # Collection schema updates
    # ------------------------------------------------------------------

    def _update_collection_schemas(
        self, client: TypesenseClient, dry_run: bool
    ) -> None:
        """
        Met à jour chaque collection pour référencer le synonym set.

        Dans Typesense v30+, le champ `synonym_sets` dans le schéma
        de la collection référence les synonym sets à utiliser.
        """
        self.stdout.write("\n📋 Mise à jour des schémas de collection...")

        for collection_name in MANAGED_COLLECTIONS:
            try:
                # Récupérer le schéma actuel
                current = client._client.collections[collection_name].retrieve()

                # Vérifier si le synonym set est déjà référencé
                current_syn_sets = current.get("synonym_sets", []) or []
                if UMS_SYNONYM_SET_NAME in current_syn_sets:
                    self.stdout.write(
                        f"  ✅ {collection_name}: synonym set déjà référencé"
                    )
                    continue

                if dry_run:
                    self.stdout.write(
                        f"   [DRY RUN] {collection_name}: ajouterait '{UMS_SYNONYM_SET_NAME}' à synonym_sets"
                    )
                    continue

                # Mettre à jour le schéma
                new_syn_sets = list(current_syn_sets) + [UMS_SYNONYM_SET_NAME]
                update_payload = {"synonym_sets": new_syn_sets}

                # Typesense v30.2: utiliser PUT /collections/{name} avec le
                # champ synonym_sets dans le payload de mise à jour
                client._client.collections[collection_name].update(update_payload)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✅ {collection_name}: synonym_sets → {new_syn_sets}"
                    )
                )

            except Exception as e:
                error_msg = str(e)
                # "No changes" ou "already" = pas d'erreur réelle
                if "already" in error_msg.lower() or "no change" in error_msg.lower():
                    self.stdout.write(f"  ✅ {collection_name}: déjà à jour")
                else:
                    self.stderr.write(f"  ❌ {collection_name}: {e}")
                    logger.exception(f"Échec mise à jour collection {collection_name}")
