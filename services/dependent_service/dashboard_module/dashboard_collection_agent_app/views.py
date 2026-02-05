from django.contrib.auth import get_user_model
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import parsers
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

from core.permissions import IsFinanceService, IsStudent, IsStudentOrFinanceService
from core.views import BaseViewSet

from .filters import (
    BankFilter,
    CollectionCorrespondenceFilter,
    FeesSheetFilter,
    PaymentFilter,
    PaymentInstallementFilter,
    PaymentPlanFilter,
    PaymentPromiseFilter,
    PaymentReminderFilter,
    WordingFilter,
)
from .models import (
    Bank,
    CollectionCorrespondence,
    FeesSheet,
    Payment,
    PaymentInstallement,
    PaymentPlan,
    PaymentPromise,
    PaymentReminder,
    Wording,
)
from .serializers import (
    BankSerializer,
    CollectionCorrespondenceSerializer,
    FeesSheetSerializer,
    PaymentInstallementSerializer,
    PaymentPlanSerializer,
    PaymentPromiseSerializer,
    PaymentReminderSerializer,
    PaymentSerializer,
    WordingSerializer,
)

User = get_user_model()


class BankViewSet(BaseViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_class = BankFilter
    search_fields = ["bank_name", "bank_abreviation", "account_number"]
    filterset_fields = ["status"]

    def get_permissions(self):
        if self.action == "list" or self.action == "retrieve":
            return [IsAuthenticated()]
        else:
            # Création, modification, suppression : seulement finance_service
            return [IsFinanceService()]

    def get_queryset(self):
        user = self.request.user

        if user.role.name == "finance_service":
            return self.queryset
        else:
            # Tous les autres rôles voient les banques actives
            return self.queryset.filter(status="active")


class WordingViewSet(BaseViewSet):
    queryset = Wording.objects.all()
    serializer_class = WordingSerializer
    permission_classes = [IsFinanceService]
    filter_backends = [SearchFilter]
    filterset_class = WordingFilter
    search_fields = ["wording_name"]


class FeesSheetViewSet(BaseViewSet):
    queryset = FeesSheet.objects.select_related(
        "class_fk",
        "class_fk__department",
        "class_fk__department__faculty",
        "department",
        "department__faculty",
        "faculty",
        "academic_year",
        "wording",
    ).all()
    serializer_class = FeesSheetSerializer
    permission_classes = [IsFinanceService]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = FeesSheetFilter
    filterset_fields = [
        "class_fk",
        "department",
        "faculty",
        "academic_year",
        "wording",
    ]
    search_fields = [
        "wording__wording_name",
        "base_amount",
    ]
    ordering_fields = [
        "base_amount",
        "wording__wording_name",
        "academic_year__academic_year",
    ]

    def get_queryset(self):
        """Filtrage personnalisé pour FeesSheet"""
        queryset = super().get_queryset()

        # Filtrage par academic_year_id
        academic_year_id = self.request.query_params.get("academic_year_id")
        if academic_year_id:
            queryset = queryset.filter(academic_year_id=academic_year_id)

        # Filtrage par wording_name
        wording_name = self.request.query_params.get("wording_name")
        if wording_name:
            queryset = queryset.filter(wording__wording_name__icontains=wording_name)

        # Filtrage par base_amount
        base_amount = self.request.query_params.get("base_amount")
        if base_amount:
            try:
                queryset = queryset.filter(base_amount=int(base_amount))
            except ValueError:
                pass  # Ignorer si pas un nombre valide

        return queryset

    def update(self, request, *args, **kwargs):
        """Mise à jour complète (PUT)"""
        from core.response_handler import error_response, success_response

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            self.perform_update(serializer)
            return success_response(
                data=serializer.data, message="FeesSheet mis à jour avec succès"
            )
        return error_response(message="Erreur de validation", errors=serializer.errors)

    def partial_update(self, request, *args, **kwargs):
        """Mise à jour partielle (PATCH)"""
        from core.response_handler import error_response, success_response

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            self.perform_update(serializer)
            return success_response(
                data=serializer.data, message="FeesSheet mis à jour avec succès"
            )
        return error_response(message="Erreur de validation", errors=serializer.errors)

    @action(detail=False, methods=["get"], url_path="grouped-options")
    def grouped_options(self, request):
        """Retourne les options groupées (classes, départements, facultés) des FeesSheets"""
        from core.response_handler import success_response

        queryset = self.get_queryset()
        classes = []
        departments = []
        faculties = []
        seen_classes = set()
        seen_departments = set()
        seen_faculties = set()

        for item in queryset:
            # Classes
            if item.class_fk and item.class_fk.id not in seen_classes:
                classes.append(
                    {
                        "id": str(item.class_fk.id),
                        "label": f"{item.class_fk.class_name} {item.class_fk.department.department_name if item.class_fk.department else ''}",
                        "value": str(item.class_fk.id),
                    }
                )
                seen_classes.add(item.class_fk.id)

            # Départements
            if item.department and item.department.id not in seen_departments:
                departments.append(
                    {
                        "id": str(item.department.id),
                        "label": item.department.department_name,
                        "value": str(item.department.id),
                    }
                )
                seen_departments.add(item.department.id)

            # Facultés
            if item.faculty and item.faculty.id not in seen_faculties:
                faculties.append(
                    {
                        "id": str(item.faculty.id),
                        "label": item.faculty.faculty_name,
                        "value": str(item.faculty.id),
                    }
                )
                seen_faculties.add(item.faculty.id)

        return success_response(
            data=[
                {
                    "group": "Classes",
                    "options": classes,
                },
                {
                    "group": "Departements",
                    "options": departments,
                },
                {
                    "group": "Faculties",
                    "options": faculties,
                },
            ],
            message="Options groupées récupérées avec succès",
        )


class PaymentInstallementViewSet(BaseViewSet):
    queryset = (
        PaymentInstallement.objects.select_related(
            "student__user",
            "payment_plan__feessheet__wording",
            "payment_plan__feessheet__academic_year",
            "payment_plan__created_by",
        )
        .prefetch_related(
            "student__inscriptions__class_fk__department__faculty",
            "student__inscriptions__academic_year",
        )
        .all()
    )
    serializer_class = PaymentInstallementSerializer
    permission_classes = [IsStudentOrFinanceService]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = PaymentInstallementFilter
    filterset_fields = [
        "payment_plan",
        "student",
        "status",
        "due_date",
        "student__inscriptions__class_fk",  # Filtrage par classe
        "student__inscriptions__class_fk__department",  # Filtrage par département
        "student__inscriptions__class_fk__department__faculty",  # Filtrage par faculté
        "student__matricule",  # Filtrage par matricule
        "student__inscriptions__academic_year",  # Filtrage par année académique
        "payment_plan__feessheet__academic_year",  # Filtrage par année académique du plan
    ]
    search_fields = [
        "student__matricule",
        "student__user__first_name",
        "student__user__last_name",
        "amount",
        "paid_amount",
        "payment_plan__feessheet__wording__wording_name",
        "status",
    ]
    ordering_fields = ["due_date", "amount"]

    def get_queryset(self):
        """Filtre les échéanciers selon le rôle de l'utilisateur"""
        user = self.request.user

        # Vérifier si l'utilisateur a un rôle
        if not hasattr(user, "role") or not user.role:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "Utilisateur sans rôle défini. Contactez l'administrateur."
            )

        if user.role.name == "finance_service":
            queryset = self.queryset
        elif user.role.name == "student":
            # Étudiant voit seulement ses échéanciers
            queryset = self.queryset.filter(student__user=user)
        else:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                f"Accès refusé. Votre rôle '{user.role.name}' n'est pas autorisé à accéder aux échéanciers de paiement. "
                "Seuls les étudiants et le service financier peuvent accéder à cette ressource."
            )

        # Filtrage personnalisé par classe (chaque classe appartient à un département)
        class_id = self.request.query_params.get("class_id")
        if class_id:
            queryset = queryset.filter(
                student__inscriptions__class_fk=class_id,
                student__inscriptions__regist_status__in=["Active", "Pending"],
            )

        # Filtrage par département
        department_id = self.request.query_params.get("department_id")
        if department_id:
            queryset = queryset.filter(
                student__inscriptions__class_fk__department=department_id,
                student__inscriptions__regist_status__in=["Active", "Pending"],
            )

        # Filtrage par faculté
        faculty_id = self.request.query_params.get("faculty_id")
        if faculty_id:
            queryset = queryset.filter(
                student__inscriptions__class_fk__department__faculty=faculty_id,
                student__inscriptions__regist_status__in=["Active", "Pending"],
            )

        return queryset.distinct()  # Éviter les doublons

    def list(self, request, *args, **kwargs):
        """Liste optimisée avec données organisées"""
        from core.response_handler import success_response

        queryset = self.filter_queryset(self.get_queryset())
        data = self._format_installments_data(queryset)
        return success_response(
            data=data, message="PaymentInstallement list retrieved successfully"
        )

    def _format_installments_data(self, installments):
        """Formate les données pour l'affichage - VERSION OPTIMISÉE"""
        data = []
        today = timezone.now().date()  # Calculer une seule fois

        for inst in installments:
            # Récupérer l'inscription la plus récente
            active_inscription = None
            inscriptions = list(inst.student.inscriptions.all())
            if inscriptions:
                # Prioriser Active, puis Pending, puis autres
                for status in ["Active", "Pending"]:
                    for inscription in inscriptions:
                        if inscription.regist_status == status:
                            active_inscription = inscription
                            break
                    if active_inscription:
                        break
                # Si aucune Active/Pending, prendre la première
                if not active_inscription:
                    active_inscription = inscriptions[0]

            data.append(
                {
                    "id": str(inst.id),
                    "student": {
                        "id": str(inst.student.id),
                        "name": f"{inst.student.user.first_name} {inst.student.user.last_name}",
                        "matricule": inst.student.matricule,
                    },
                    "class_info": (
                        {
                            "id": str(active_inscription.class_fk.id),
                            "name": active_inscription.class_fk.class_name,
                            "department": (
                                active_inscription.class_fk.department.department_name
                                if active_inscription.class_fk.department
                                else None
                            ),
                            "faculty": (
                                active_inscription.class_fk.department.faculty.faculty_name
                                if active_inscription.class_fk.department
                                and active_inscription.class_fk.department.faculty
                                else None
                            ),
                        }
                        if active_inscription and active_inscription.class_fk
                        else None
                    ),
                    "payment_plan": {
                        "id": str(inst.payment_plan.id),
                        "total_amount": inst.payment_plan.total_amount,
                        "monthly_amount": inst.payment_plan.monthly_amount,
                        "start_date": inst.payment_plan.start_date,
                        "end_date": inst.payment_plan.end_date,
                        "status": inst.payment_plan.status,
                        "description": inst.payment_plan.description,
                        "wording": (
                            inst.payment_plan.feessheet.wording.wording_name
                            if inst.payment_plan.feessheet
                            else None
                        ),
                    },
                    "financial_info": {
                        "amount": inst.amount,
                        "paid_amount": inst.paid_amount,
                        "remaining_amount": inst.amount - inst.paid_amount,
                        "completion_percentage": (
                            round((inst.paid_amount / inst.amount) * 100, 2)
                            if inst.amount > 0
                            else 0
                        ),
                    },
                    "status_info": {
                        "status": inst.status,
                        "status_display": inst.get_status_display(),
                        "is_overdue": inst.status == "overdue",
                        "days_overdue": (
                            (today - inst.due_date).days
                            if inst.status == "overdue"
                            else 0
                        ),
                    },
                    "dates": {
                        "due_date": inst.due_date,
                        "paid_date": inst.paid_date,
                        "created_at": inst.created_at,
                    },
                }
            )

        return data

    @action(detail=False, methods=["get"], permission_classes=[IsFinanceService])
    def available_filters(self, request):
        """Retourne les options de filtrage disponibles"""
        from core.response_handler import success_response
        from services.core_service.academic_module.class_app.models import Class
        from services.core_service.academic_module.department_app.models import (
            Department,
        )
        from services.core_service.academic_module.faculty_app.models import Faculty

        # Classes avec des étudiants ayant des échéanciers
        classes = (
            Class.objects.filter(
                inscriptions__student__paymentinstallement__isnull=False,
                inscriptions__regist_status__in=["Active", "Pending"],
            )
            .distinct()
            .values("id", "class_name", "department__department_name")
        )

        # Départements avec des étudiants ayant des échéanciers
        departments = (
            Department.objects.filter(
                classes__inscriptions__student__paymentinstallement__isnull=False,
                classes__inscriptions__regist_status__in=["Active", "Pending"],
            )
            .distinct()
            .values("id", "department_name", "faculty__faculty_name")
        )

        # Facultés avec des étudiants ayant des échéanciers
        faculties = (
            Faculty.objects.filter(
                departments__classes__inscriptions__student__paymentinstallement__isnull=False,
                departments__classes__inscriptions__regist_status__in=[
                    "Active",
                    "Pending",
                ],
            )
            .distinct()
            .values("id", "faculty_name")
        )

        return success_response(
            data={
                "classes": list(classes),
                "departments": list(departments),
                "faculties": list(faculties),
            },
            message="Available filters retrieved successfully",
        )

    @action(detail=False, methods=["get"], permission_classes=[IsFinanceService])
    def unpaid_installments(self, request):
        """Échéanciers non payés (pending + overdue)"""
        from core.response_handler import success_response

        queryset = self.filter_queryset(self.get_queryset()).filter(
            status__in=["pending", "overdue"]
        )
        data = self._format_installments_data(queryset)
        return success_response(
            data=data, message="Unpaid installments retrieved successfully"
        )

    @action(detail=False, methods=["get"], permission_classes=[IsFinanceService])
    def incomplete_payments_by_class(self, request):
        """Étudiants qui n'ont pas fini leurs paiements par classe"""
        from core.response_handler import error_response, success_response

        class_id = request.query_params.get("class_id")
        if not class_id:
            return error_response(message="class_id est requis", status_code=400)

        # Étudiants avec des échéanciers non terminés dans cette classe
        queryset = (
            self.get_queryset()
            .filter(
                student__inscriptions__class_fk=class_id,
                student__inscriptions__regist_status__in=["Active", "Pending"],
                status__in=["pending", "overdue"],
            )
            .distinct()
        )
        data = self._format_installments_data(queryset)
        return success_response(
            data=data, message="Incomplete payments by class retrieved successfully"
        )

    @action(detail=False, methods=["get"], permission_classes=[IsFinanceService])
    def overdue_payments(self, request):
        """Échéanciers en retard seulement"""
        from core.response_handler import success_response

        queryset = self.filter_queryset(self.get_queryset()).filter(status="overdue")
        data = self._format_installments_data(queryset)
        return success_response(
            data=data, message="Overdue payments retrieved successfully"
        )


class PaymentReminderViewSet(BaseViewSet):
    queryset = PaymentReminder.objects.all()
    serializer_class = PaymentReminderSerializer
    permission_classes = [IsFinanceService]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = PaymentReminderFilter
    filterset_fields = ["student", "reminder_type", "status"]
    search_fields = [
        "student__matricule",
        "student__user__first_name",
        "student__user__last_name",
        "reminder_type",
        "amount_due",
        "message",
    ]
    ordering_fields = ["sent_at"]


class PaymentPlanViewSet(BaseViewSet):
    queryset = PaymentPlan.objects.select_related(
        "feessheet__wording",
        "feessheet__class_fk",
        "feessheet__class_fk__department",
        "feessheet__class_fk__department__faculty",
        "feessheet__department",
        "feessheet__department__faculty",
        "feessheet__faculty",
        "feessheet__academic_year",
    ).all()
    serializer_class = PaymentPlanSerializer
    permission_classes = [IsStudentOrFinanceService]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = PaymentPlanFilter
    filterset_fields = ["feessheet", "status", "created_by"]
    search_fields = [
        "feessheet__wording__wording_name",
        "description",
        "total_amount",
        "status",
    ]
    ordering_fields = ["start_date", "total_amount"]

    def get_queryset(self):
        """Filtre les plans de paiement selon le rôle de l'utilisateur"""
        user = self.request.user

        if not hasattr(user, "role") or not user.role:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Utilisateur sans rôle défini.")

        if user.role.name in ["finance_service", "student_service"]:
            # Finance et service étudiant voient tous les plans
            return self.queryset
        elif user.role.name in ["student", "guest"]:
            # Étudiant et invité voient seulement les plans applicables à sa classe/département/faculté
            try:
                from services.core_service.student_module.student_profile_app.models import (
                    Student,
                )

                student = Student.objects.get(user=user)
                return PaymentPlan.get_plans_for_student(student)
            except Student.DoesNotExist:
                from rest_framework.exceptions import PermissionDenied

                raise PermissionDenied("Profil étudiant non trouvé.")
        else:
            # Tous les autres rôles voient tous les plans
            return self.queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        from rest_framework import status

        from core.response_handler import success_response, validate_serializer

        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error
        serializer.save(created_by=request.user)
        return success_response(
            data=serializer.data,
            message=f"{self.queryset.model.__name__} created successfully",
            status_code=status.HTTP_201_CREATED,
        )


class PaymentPromiseViewSet(BaseViewSet):
    queryset = PaymentPromise.objects.all()
    serializer_class = PaymentPromiseSerializer
    permission_classes = [IsStudent]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentPromiseFilter
    filterset_fields = ["student", "status", "promised_date"]
    ordering_fields = ["promised_date", "promised_amount"]


class PaymentViewSet(BaseViewSet):
    queryset = Payment.objects.select_related(
        "paymentplan__feessheet__wording",
        "paymentplan__feessheet__academic_year",
        "bank",
        "inscription__student__user",
        "inscription__academic_year",
        "inscription__class_fk",
        "user",
        "verified_by",
    ).all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = PaymentFilter
    filterset_fields = [
        "paymentplan",
        "payment_method",
        "payment_status",
        "bank",
        "inscription",
        "user",
    ]
    search_fields = [
        "inscription__student__matricule",
        "inscription__student__user__first_name",
        "inscription__student__user__last_name",
        "amount_paid",
        "transaction_code",
        "payment_method",
        "payment_status",
        "description",
    ]
    ordering_fields = ["payment_date", "amount_paid"]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_permissions(self):
        if self.action == "create":
            # Création : tous les utilisateurs authentifiés
            return [IsAuthenticated()]
        elif self.action in ["update", "partial_update"]:
            # Modification : seulement finance_service
            return [IsFinanceService()]
        else:
            # Lecture : tous les utilisateurs authentifiés
            return [IsAuthenticated()]

    def get_queryset(self):
        """Filtre les paiements selon le rôle de l'utilisateur"""
        user = self.request.user
        base_queryset = self.queryset.select_related("paymentplan", "bank")

        if user.role.name == "finance_service":
            return base_queryset
        elif user.role.name in ["student", "guest"]:
            return base_queryset.filter(
                inscription__student__user=user,
                inscription__regist_status__in=["Active", "Pending"],
            )
        elif user.role.name == "student_service":
            # Service aux étudiants voit tous les paiements
            return base_queryset
        else:
            # Tous les autres rôles voient tous les paiements
            return base_queryset

    def create(self, request, *args, **kwargs):
        import logging

        logger = logging.getLogger(__name__)

        logger.debug(f"PaymentSerializer - données reçues: {request.data}")
        logger.debug(f"PaymentSerializer - clés: {list(request.data.keys())}")

        serializer = self.get_serializer(data=request.data)
        from rest_framework import status

        from core.response_handler import success_response, validate_serializer

        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        serializer.save(user=request.user)

        return success_response(
            data=serializer.data,
            message=f"{self.queryset.model.__name__} created successfully",
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        """Mise à jour complète (PUT) d'un paiement par ID"""
        from core.response_handler import error_response, success_response

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)

        if serializer.is_valid():
            self.perform_update(serializer)
            return success_response(
                data=serializer.data, message="Paiement mis à jour avec succès"
            )
        return error_response(message="Erreur de validation", errors=serializer.errors)

    def partial_update(self, request, *args, **kwargs):
        """Mise à jour partielle (PATCH) d'un paiement par ID"""
        from core.response_handler import error_response, success_response

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            self.perform_update(serializer)
            return success_response(
                data=serializer.data, message="Paiement mis à jour avec succès"
            )
        return error_response(message="Erreur de validation", errors=serializer.errors)


class CollectionCorrespondenceViewSet(BaseViewSet):
    queryset = CollectionCorrespondence.objects.all()
    serializer_class = CollectionCorrespondenceSerializer
    permission_classes = [IsFinanceService]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CollectionCorrespondenceFilter
    filterset_fields = ["student", "correspondence_type"]
    search_fields = ["subject", "content"]
    ordering_fields = ["sent_at"]
