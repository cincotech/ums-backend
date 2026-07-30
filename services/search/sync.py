import logging
from typing import Any

from django.apps import apps
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from . import builders
from .builders.base import sanitize, stable_created_at
from .client import TypesenseClient
from .schemas import MODEL_TO_COLLECTION

logger = logging.getLogger(__name__)

# Only these models own a Typesense collection. Other academic models
# (ClassGroup, TypeFormation, Semester, Attribution, Suggestion, AcademicYear,
# UniversityAdmin, UniversityDegree) are indexed indirectly through the
# relation traversal below and must NOT have their own save signals.
INDEXED_MODEL_LABELS = (
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
    ("result_app", "Session"),
    ("result_app", "Result"),
    ("dashboard_academic_secretary_app", "JurySession"),
    ("authorization_app", "Profile"),
)


class DocumentSyncer:
    """Synchronise automatiquement les modifications Django vers Typesense.

    Each indexed model gets a dedicated, flat document builder that traverses
    the relations Typesense cannot traverse itself (Typesense documents are
    flat). Builders only emit schema-conformant fields; missing attributes are
    simply omitted rather than written as null (Typesense rejects null on
    non-optional string fields and would fail the whole upsert).
    """

    def __init__(self):
        self.client = TypesenseClient()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def index_instance(self, instance) -> None:
        """Indexe une instance Django unique."""
        if not self.client.enabled:
            return
        try:
            collection = self._get_collection(instance.__class__)
            if not collection:
                logger.debug(
                    "No collection for %s, skipping index",
                    instance.__class__.__name__,
                )
                return
            document = self._serialize_instance(instance)
            if not document:
                return
            self.client.index_document(collection, document)
            logger.debug("Indexed %s %s", instance.__class__.__name__, instance.id)
        except Exception as e:
            logger.error(
                "Failed to index %s %s: %s",
                instance.__class__.__name__,
                getattr(instance, "id", "?"),
                e,
            )

    def delete_instance(self, instance) -> None:
        """Supprime un document Typesense."""
        if not self.client.enabled:
            return
        try:
            collection = self._get_collection(instance.__class__)
            if not collection:
                return
            self.client.delete_document(collection, str(instance.id))
            logger.debug("Deleted %s %s", instance.__class__.__name__, instance.id)
        except Exception as e:
            logger.error(
                "Failed to delete %s %s: %s",
                instance.__class__.__name__,
                getattr(instance, "id", "?"),
                e,
            )

    # ------------------------------------------------------------------
    # Collection resolution
    # ------------------------------------------------------------------

    def _get_collection(self, model: type) -> str | None:
        """Retourne le nom de la collection pour un modèle, ou None."""
        return MODEL_TO_COLLECTION.get(model.__name__)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def _serialize_instance(self, instance) -> dict[str, Any]:
        """Build a flat, schema-conformant document for the instance."""
        model_name = instance.__class__.__name__
        builder = self._BUILDERS.get(model_name)
        if builder is None:
            logger.warning("No document builder for %s", model_name)
            return {}

        try:
            document = builder(instance)
        except Exception as e:
            logger.error(
                "Error building document for %s %s: %s",
                model_name,
                getattr(instance, "id", "?"),
                e,
            )
            return {}

        # `id` and a stable `created_at` are always present.
        document["id"] = str(instance.id)
        document.setdefault("created_at", stable_created_at(instance))
        document.setdefault("is_deleted", False)

        return sanitize(document, model_name, MODEL_TO_COLLECTION)

    # ------------------------------------------------------------------
    # Per-model flat document builders — delegated to services.search.builders
    # ------------------------------------------------------------------

    # Dispatch table
    _BUILDERS = {
        "Course": builders.build_course,
        "Module": builders.build_module,
        "Teacher": builders.build_teacher,
        "Class": builders.build_class,
        "ClassGroup": builders.build_class_group,
        "Department": builders.build_department,
        "Faculty": builders.build_faculty,
        "Inscription": builders.build_inscription,
        "Student": builders.build_student,
        "University": builders.build_university,
        "User": builders.build_user,
        "Session": builders.build_session,
        "Result": builders.build_result,
        "JurySession": builders.build_jury_session,
        "Profile": builders.build_profile,
    }


# Instance globale du syncer
syncer = DocumentSyncer()


# --- Signaux pour les modèles académiques ---


def get_academic_models():
    """Retourne uniquement les modèles qui possèdent une collection."""
    models = []
    for app_label, model_name in INDEXED_MODEL_LABELS:
        try:
            models.append(apps.get_model(app_label, model_name))
        except LookupError:
            logger.warning("Model %s.%s not found, skipping", app_label, model_name)
    return models


def register_signals():
    """Enregistre post_save/post_delete pour les 7 modèles indexés."""
    for model in get_academic_models():
        if getattr(model, "_typesense_signals_registered", False):
            continue
        post_save.connect(
            lambda sender, instance, **kwargs: syncer.index_instance(instance),
            sender=model,
            weak=False,
        )
        post_delete.connect(
            lambda sender, instance, **kwargs: syncer.delete_instance(instance),
            sender=model,
            weak=False,
        )
        model._typesense_signals_registered = True
        logger.debug("Typesense signals registered for %s", model.__name__)


# L'enregistrement des signaux est appelé depuis apps.py::SearchConfig.ready()
# pour éviter l'erreur "Apps aren't loaded yet"


# --- Signaux croisés pour les relations ---


@receiver(post_save)
def handle_related_updates(sender, instance, **kwargs):
    """Met à jour les documents dépendants lorsqu'une relation change.

    When a related object changes, the denormalized fields stored on dependent
    documents go stale. We re-index every dependent document so the flat
    search fields stay in sync.
    """
    if not syncer.client.enabled:
        return

    sender_name = getattr(sender, "__name__", None)

    # Module mis à jour → mettre à jour les cours associés
    if sender_name == "Module":
        try:
            Course = apps.get_model("course_app", "Course")
            for course in Course.objects.filter(module=instance):
                syncer.index_instance(course)
            logger.debug("Updated courses for module %s", instance.id)
        except LookupError:
            pass
        return

    # Department mis à jour → mettre à jour cours, modules, classes, class_groups et inscriptions
    if sender_name == "Department":
        try:
            Course = apps.get_model("course_app", "Course")
            Module = apps.get_model("module_app", "Module")
            Class = apps.get_model("class_app", "Class")
            ClassGroup = apps.get_model("class_app", "ClassGroup")
            Inscription = apps.get_model("inscription_app", "Inscription")
            for course in Course.objects.filter(module__class_fk__department=instance):
                syncer.index_instance(course)
            for module in Module.objects.filter(class_fk__department=instance):
                syncer.index_instance(module)
            for class_obj in Class.objects.filter(department=instance):
                syncer.index_instance(class_obj)
            for cg in ClassGroup.objects.filter(class_fk__department=instance):
                syncer.index_instance(cg)
            for ins in Inscription.objects.filter(class_fk__department=instance):
                syncer.index_instance(ins)
            logger.debug("Updated dependent docs for department %s", instance.id)
        except LookupError:
            pass
        return

    # Faculty mis à jour → mettre à jour départements, modules, cours, classes, class_groups, inscriptions
    if sender_name == "Faculty":
        try:
            Department = apps.get_model("department_app", "Department")
            Module = apps.get_model("module_app", "Module")
            Course = apps.get_model("course_app", "Course")
            Class = apps.get_model("class_app", "Class")
            ClassGroup = apps.get_model("class_app", "ClassGroup")
            Inscription = apps.get_model("inscription_app", "Inscription")
            for dept in Department.objects.filter(faculty=instance):
                syncer.index_instance(dept)
            for module in Module.objects.filter(class_fk__department__faculty=instance):
                syncer.index_instance(module)
            for course in Course.objects.filter(
                module__class_fk__department__faculty=instance
            ):
                syncer.index_instance(course)
            for class_obj in Class.objects.filter(department__faculty=instance):
                syncer.index_instance(class_obj)
            for cg in ClassGroup.objects.filter(class_fk__department__faculty=instance):
                syncer.index_instance(cg)
            for ins in Inscription.objects.filter(
                class_fk__department__faculty=instance
            ):
                syncer.index_instance(ins)
            logger.debug("Updated dependent docs for faculty %s", instance.id)
        except LookupError:
            pass
        return

    # University mis à jour → mettre à jour facultés, départements, etc.
    if sender_name == "University":
        try:
            Faculty = apps.get_model("faculty_app", "Faculty")
            Department = apps.get_model("department_app", "Department")
            Class = apps.get_model("class_app", "Class")
            ClassGroup = apps.get_model("class_app", "ClassGroup")
            Module = apps.get_model("module_app", "Module")
            Course = apps.get_model("course_app", "Course")
            Inscription = apps.get_model("inscription_app", "Inscription")
            for faculty in Faculty.objects.filter(university=instance):
                syncer.index_instance(faculty)
            for dept in Department.objects.filter(faculty__university=instance):
                syncer.index_instance(dept)
            for class_obj in Class.objects.filter(
                department__faculty__university=instance
            ):
                syncer.index_instance(class_obj)
            for cg in ClassGroup.objects.filter(
                class_fk__department__faculty__university=instance
            ):
                syncer.index_instance(cg)
            for module in Module.objects.filter(
                class_fk__department__faculty__university=instance
            ):
                syncer.index_instance(module)
            for course in Course.objects.filter(
                module__class_fk__department__faculty__university=instance
            ):
                syncer.index_instance(course)
            for ins in Inscription.objects.filter(
                class_fk__department__faculty__university=instance
            ):
                syncer.index_instance(ins)
            logger.debug("Updated dependent docs for university %s", instance.id)
        except LookupError:
            pass
        return

    # Class mis à jour → mettre à jour les modules, cours, class_groups et inscriptions liés
    if sender_name == "Class":
        try:
            Module = apps.get_model("module_app", "Module")
            Course = apps.get_model("course_app", "Course")
            ClassGroup = apps.get_model("class_app", "ClassGroup")
            Inscription = apps.get_model("inscription_app", "Inscription")
            for module in Module.objects.filter(class_fk=instance):
                syncer.index_instance(module)
            for course in Course.objects.filter(module__class_fk=instance):
                syncer.index_instance(course)
            for cg in ClassGroup.objects.filter(class_fk=instance):
                syncer.index_instance(cg)
            for ins in Inscription.objects.filter(class_fk=instance):
                syncer.index_instance(ins)
            logger.debug("Updated dependent docs for class %s", instance.id)
        except LookupError:
            pass
        return

    # User mis à jour → mettre à jour le teacher lié (full_name / email / phone)
    if sender_name == "User":
        try:
            Teacher = apps.get_model("teacher_app", "Teacher")
            for teacher in Teacher.objects.filter(user=instance):
                syncer.index_instance(teacher)
        except LookupError:
            pass
        return

    # Teacher mis à jour → mettre à jour l'utilisateur lié
    if sender_name == "Teacher":
        try:
            syncer.index_instance(instance.user)
        except Exception:
            pass
        return

    # Student mis à jour → mettre à jour l'utilisateur lié et les inscriptions
    if sender_name == "Student":
        try:
            syncer.index_instance(instance.user)
        except Exception:
            pass
        try:
            Inscription = apps.get_model("inscription_app", "Inscription")
            for ins in Inscription.objects.filter(student=instance):
                syncer.index_instance(ins)
        except LookupError:
            pass
        return

    # Inscription mis à jour → mettre à jour l'étudiant lié (car Student utilise la dernière inscription)
    if sender_name == "Inscription":
        try:
            syncer.index_instance(instance.student)
        except Exception:
            pass
        return

    # ClassGroup mis à jour → mettre à jour les inscriptions liées (car Inscription stocke class_group_name)
    if sender_name == "ClassGroup":
        try:
            Inscription = apps.get_model("inscription_app", "Inscription")
            for ins in Inscription.objects.filter(class_group=instance):
                syncer.index_instance(ins)
        except LookupError:
            pass
        return

    # UniversityAdmin mis à jour → mettre à jour l'utilisateur lié
    if sender_name == "UniversityAdmin":
        try:
            syncer.index_instance(instance.user)
        except Exception:
            pass
        return

    # Country mis à jour → mettre à jour les universités liées
    if sender_name == "Country":
        try:
            University = apps.get_model("university_app", "University")
            for university in University.objects.filter(country=instance):
                syncer.index_instance(university)
        except LookupError:
            pass


# Fonction utilitaire pour forcer la réindexation d'un modèle
def reindex_model(model_name: str, batch_size: int = 100) -> None:
    """Réindexe tous les documents d'un modèle donné."""
    label_map = dict(INDEXED_MODEL_LABELS)
    app_label = label_map.get(model_name)
    if not app_label:
        logger.error("Model %s is not indexed.", model_name)
        return

    try:
        model = apps.get_model(app_label, model_name)
        queryset = model.objects.all()
        count = queryset.count()
        logger.info("Reindexing %s (%s documents)...", model_name, count)

        for i in range(0, count, batch_size):
            batch = queryset[i : i + batch_size]
            for instance in batch:
                syncer.index_instance(instance)
            logger.info("  %s/%s", min(i + batch_size, count), count)

        logger.info("✅ %s reindexed successfully.", model_name)
    except LookupError:
        logger.error("❌ Model %s not found.", model_name)
    except Exception as e:
        logger.error("❌ Error reindexing %s: %s", model_name, e)
