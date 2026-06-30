from django.contrib.auth import get_user_model
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import parsers, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

from core.permissions import (
    IsFinanceOrDirection,
    IsFinanceService,
    IsStudentOrFinance,
)
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
    Bordereau,
    BordereauLine,
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
    BordereauLineSerializer,
    BordereauSerializer,
    CollectionCorrespondenceSerializer,
    FeesSheetSerializer,
    PaymentInstallementSerializer,
    PaymentPlanSerializer,
    PaymentPromiseSerializer,
    PaymentReminderSerializer,
    PaymentSerializer,
    WordingSerializer,
)
from .finance_dashboard_service import FinanceDashboardService

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
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]

    def get_permissions(self):
        if self.action in ("list", "retrieve", "grouped_options"):
            return [IsStudentOrFinance()]
        return [IsFinanceService()]

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

        # Support d'alias frontend
        department_fk = self.request.query_params.get("department_fk")
        if department_fk:
            queryset = queryset.filter(department=department_fk)

        faculty_fk = self.request.query_params.get("faculty_fk")
        if faculty_fk:
            queryset = queryset.filter(faculty=faculty_fk)

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
    permission_classes = [IsStudentOrFinance]
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

    def get_permissions(self):
        # Respecter les permissions d'actions personnalisées si définies
        action_method = getattr(self, self.action, None)
        if action_method and hasattr(action_method, "permission_classes"):
            return [perm() for perm in action_method.permission_classes]

        if self.action in ["list", "retrieve"]:
            permission_classes = [IsStudentOrFinance]
        else:
            permission_classes = [IsFinanceService]

        return [perm() for perm in permission_classes]

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
        elif user.role.name in ["student", "guest"]:
            # Étudiant voit seulement ses échéanciers
            queryset = self.queryset.filter(student__user=user)
        elif user.role.name == "student_service":
            queryset = self.queryset
        else:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                f"Accès refusé. Votre rôle '{user.role.name}' n'est pas autorisé à accéder aux échéanciers de paiement. "
                "Seuls les étudiants et le service financier peuvent accéder à cette ressource."
            )

        # Filtrage par année académique
        academic_year_id = self.request.query_params.get("academic_year_id")
        if academic_year_id:
            queryset = queryset.filter(
                student__inscriptions__academic_year=academic_year_id,
                student__inscriptions__regist_status__in=["Active", "Pending"],
            )

        # Filtrage personnalisé par classe (chaque classe appartient à un département)
        class_id = self.request.query_params.get("class_id") or self.request.query_params.get(
            "class_fk"
        )
        if class_id:
            queryset = queryset.filter(
                student__inscriptions__class_fk=class_id,
                student__inscriptions__regist_status__in=["Active", "Pending"],
            )

        # Filtrage par département
        department_id = self.request.query_params.get(
            "department_id"
        ) or self.request.query_params.get("department_fk")
        if department_id:
            queryset = queryset.filter(
                student__inscriptions__class_fk__department=department_id,
                student__inscriptions__regist_status__in=["Active", "Pending"],
            )

        # Filtrage par faculté
        faculty_id = self.request.query_params.get("faculty_id") or self.request.query_params.get(
            "faculty_fk"
        )
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
                        "matricule": inst.student.get_active_matricule().matricule
                        if inst.student.get_active_matricule()
                        else None,
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
    permission_classes = [IsStudentOrFinance]
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

    def get_permissions(self):
        # Respecter les permissions d'actions personnalisées si définies
        action_method = getattr(self, self.action, None)
        if action_method and hasattr(action_method, "permission_classes"):
            return [perm() for perm in action_method.permission_classes]

        if self.action in ["list", "retrieve"]:
            permission_classes = [IsStudentOrFinance]
        else:
            permission_classes = [IsFinanceService]

        return [perm() for perm in permission_classes]

    def get_queryset(self):
        """Filtre les plans de paiement selon le rôle de l'utilisateur"""
        user = self.request.user

        if not hasattr(user, "role") or not user.role:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Utilisateur sans rôle défini.")

        # Utiliser la méthode du modèle pour filtrer selon le rôle
        queryset = PaymentPlan.get_plans_for_user(user)

        # Filtrage optionnel par année académique
        academic_year_id = self.request.query_params.get("academic_year_id")
        if academic_year_id:
            queryset = queryset.filter(feessheet__academic_year=academic_year_id)

        # Support des alias frontend
        class_id = self.request.query_params.get("class_id") or self.request.query_params.get(
            "class_fk"
        )
        if class_id:
            queryset = queryset.filter(feessheet__class_fk=class_id)

        department_id = self.request.query_params.get(
            "department_id"
        ) or self.request.query_params.get("department_fk")
        if department_id:
            queryset = queryset.filter(feessheet__department=department_id)

        faculty_id = self.request.query_params.get("faculty_id") or self.request.query_params.get(
            "faculty_fk"
        )
        if faculty_id:
            queryset = queryset.filter(feessheet__faculty=faculty_id)

        return queryset

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
    permission_classes = [IsStudentOrFinance]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentPromiseFilter
    filterset_fields = ["student", "status", "promised_date"]
    ordering_fields = ["promised_date", "promised_amount"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsStudentOrFinance]
        else:
            permission_classes = [IsFinanceService]

        return [perm() for perm in permission_classes]

    def get_queryset(self):
        """Limiter les promesses pour les étudiants à leurs propres données."""
        user = self.request.user

        if user.role.name in ["student", "guest"]:
            return self.queryset.filter(student__user=user)
        if user.role.name in ["finance_service", "student_service"]:
            return self.queryset

        from rest_framework.exceptions import PermissionDenied

        raise PermissionDenied("Accès refusé à cette ressource.")


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
        "verified_by",
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
    ordering_fields = ["payment_date", "amount_paid", "reception_date", "verified_at"]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_permissions(self):
        if self.action == "create":
            # Création : tous les utilisateurs authentifiés
            permission_classes = [IsAuthenticated]
        elif self.action in ["update", "partial_update", "destroy"]:
            # Modification/Suppression : seulement finance_service
            permission_classes = [IsFinanceService]
        else:
            # Lecture : étudiants (leurs données) + finance
            permission_classes = [IsStudentOrFinance]

        return [perm() for perm in permission_classes]

    def get_queryset(self):
        """Filtre les paiements selon le rôle de l'utilisateur avec filtres personnalisés"""
        user = self.request.user
        base_queryset = self.queryset.select_related("paymentplan", "bank")

        # Filtrage par rôle
        if user.role.name == "finance_service":
            queryset = base_queryset
        elif user.role.name in ["student", "guest"]:
            queryset = base_queryset.filter(
                inscription__student__user=user,
                inscription__regist_status__in=["Active", "Pending"],
            )
        elif user.role.name == "student_service":
            queryset = base_queryset
        else:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                f"Accès refusé. Votre rôle '{user.role.name}' n'est pas autorisé à accéder aux paiements."
            )

        # Filtres personnalisés supplémentaires
        student_id = self.request.query_params.get("student_id")
        if student_id:
            queryset = queryset.filter(inscription__student__id=student_id)

        class_id = self.request.query_params.get("class_id") or self.request.query_params.get(
            "class_fk"
        )
        if class_id:
            queryset = queryset.filter(
                inscription__class_fk__id=class_id,
                inscription__regist_status__in=["Active", "Pending"],
            )

        department_id = self.request.query_params.get(
            "department_id"
        ) or self.request.query_params.get("department_fk")
        if department_id:
            queryset = queryset.filter(
                inscription__class_fk__department__id=department_id,
                inscription__regist_status__in=["Active", "Pending"],
            )

        faculty_id = self.request.query_params.get("faculty_id") or self.request.query_params.get(
            "faculty_fk"
        )
        if faculty_id:
            queryset = queryset.filter(
                inscription__class_fk__department__faculty__id=faculty_id,
                inscription__regist_status__in=["Active", "Pending"],
            )

        academic_year_id = self.request.query_params.get("academic_year_id")
        if academic_year_id:
            queryset = queryset.filter(inscription__academic_year__id=academic_year_id)

        # Filtrage par nom d'année académique (ex: 2024-2025)
        academic_year = self.request.query_params.get("academic_year")
        if academic_year:
            queryset = queryset.filter(
                inscription__academic_year__academic_year=academic_year
            )

        # Filtrage par plage de dates
        payment_date_from = self.request.query_params.get("payment_date_from")
        if payment_date_from:
            queryset = queryset.filter(payment_date__gte=payment_date_from)

        payment_date_to = self.request.query_params.get("payment_date_to")
        if payment_date_to:
            queryset = queryset.filter(payment_date__lte=payment_date_to)

        # Filtrage par montant
        amount_min = self.request.query_params.get("amount_min")
        if amount_min:
            queryset = queryset.filter(amount_paid__gte=amount_min)

        amount_max = self.request.query_params.get("amount_max")
        if amount_max:
            queryset = queryset.filter(amount_paid__lte=amount_max)

        # Ordre par défaut pour éviter UnorderedObjectListWarning
        return queryset.distinct().order_by("-payment_date", "-verified_at", "-id")

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
    @action(detail=False, methods=['get'], url_path='by-inscription/(?P<inscription_id>[^/.]+)')
    def by_inscription(self, request, inscription_id=None):
        from core.response_handler import error_response, success_response
        """
        Récupère tous les paiements liés à une inscription spécifique
        Usage: /api/payments/by-inscription/<inscription_id>/
        """
        # On réutilise le queryset de base qui contient déjà les select_related
        # pour garder les performances optimales (pas de requêtes N+1)
        if not inscription_id:
             return error_response(message="inscription_id est requis", status_code=400)
        payments = self.get_queryset().filter(inscription_id=inscription_id)
        
        serializer = self.get_serializer(payments, many=True)
        
        return success_response(
            data=serializer.data,
            message=f"Paiements récupérés pour l'inscription {inscription_id}"
        )
    @action(detail=False, methods=['get'], url_path='by-inscription/(?P<inscription_id>[^/.]+)')
    def by_inscription(self, request, inscription_id=None):
        from core.response_handler import error_response, success_response
        """
        Récupère tous les paiements liés à une inscription spécifique
        Usage: /api/payments/by-inscription/<inscription_id>/
        """
        
        # On réutilise le queryset de base qui contient déjà les select_related
        # pour garder les performances optimales (pas de requêtes N+1)
        if not inscription_id:
            return error_response(message="inscription_id est requis", status_code=400)
        payments = self.get_queryset().filter(inscription_id=inscription_id)
        
        serializer = self.get_serializer(payments, many=True)
        
        return success_response(
            data=serializer.data,
            message=f"Paiements récupérés pour l'inscription {inscription_id}"
        )


class CollectionCorrespondenceViewSet(BaseViewSet):
    queryset = CollectionCorrespondence.objects.all()
    serializer_class = CollectionCorrespondenceSerializer
    permission_classes = [IsFinanceService]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CollectionCorrespondenceFilter
    filterset_fields = ["student", "correspondence_type"]
    search_fields = ["subject", "content"]
    ordering_fields = ["sent_at"]


class FinanceDashboardAPIView(viewsets.ViewSet):
    """Overview KPI for finance + direction dashboard."""

    permission_classes = [IsFinanceOrDirection]

    @action(detail=False, methods=["get"])
    def overview(self, request):
        from core.response_handler import success_response

        university = getattr(request.user, "university", None)
        if not university:
            try:
                university = request.user.university_admin.university
            except Exception:
                university = None
        if not university:
            return success_response(
                data=FinanceDashboardService._empty_payload(),
                message="University not found for user",
            )

        academic_year_id = request.query_params.get("academic_year_id")
        period = request.query_params.get("period")
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        data = FinanceDashboardService.get_overview(
            university=university,
            academic_year_id=academic_year_id,
            period=period,
            date_from=date_from,
            date_to=date_to,
        )
        return success_response(data=data, message="Finance overview retrieved successfully")


class BordereauViewSet(BaseViewSet):
    queryset = Bordereau.objects.select_related(
        "bank", "student__user", "created_by", "verified_by", "parent"
    ).prefetch_related("lines__feessheet__wording", "lines__payment")
    serializer_class = BordereauSerializer
    parser_classes = [parsers.MultiPartParser, parsers.JSONParser]

    def get_permissions(self):
        if self.action in ("verify", "update", "partial_update", "destroy", "split"):
            return [IsFinanceService()]
        # list, retrieve, create → student_service + finance_service
        return [IsStudentOrFinance()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        role = getattr(getattr(user, "role", None), "name", None)
        if role == "student":
            qs = qs.filter(student__user=user)
        student_id = self.request.query_params.get("student_id")
        if student_id:
            qs = qs.filter(student_id=student_id)
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-created_at")

    @action(detail=True, methods=["post"], url_path="verify")
    def verify(self, request, pk=None):
        from core.response_handler import success_response, error_response

        bordereau = self.get_object()
        role = getattr(getattr(request.user, "role", None), "name", None)
        if role != "finance_service":
            return error_response(
                message="Seul le service financier peut vérifier un bordereau.",
                status_code=403,
            )
        bordereau.status = "verified"
        bordereau.verified_by = request.user
        bordereau.verified_at = timezone.now()
        bordereau.save()
        return success_response(
            data=BordereauSerializer(bordereau, context={"request": request}).data,
            message="Bordereau vérifié.",
        )

    @action(detail=True, methods=["post"], url_path="split")
    def split(self, request, pk=None):
        """Créer des bordereaux enfants à partir d'un bordereau parent."""
        from core.response_handler import success_response, error_response

        parent = self.get_object()
        lines_data = request.data.get("splits", [])
        if not lines_data:
            return error_response(message="Aucune répartition fournie.", status_code=400)

        total = sum(float(s.get("amount", 0)) for s in lines_data)
        if round(total, 2) != round(float(parent.amount), 2):
            return error_response(
                message=f"La somme des fractions ({total}) ne correspond pas au montant du bordereau ({parent.amount}).",
                status_code=400,
            )

        children = []
        for s in lines_data:
            child = Bordereau.objects.create(
                numero=parent.numero,
                amount=s["amount"],
                bank=parent.bank,
                student=parent.student,
                payment_date=parent.payment_date,
                payment_method=parent.payment_method,
                status="pending",
                parent=parent,
                notes=s.get("notes"),
                created_by=request.user,
            )
            children.append(child)

        parent.status = "split"
        parent.save()

        return success_response(
            data=BordereauSerializer(children, many=True, context={"request": request}).data,
            message="Bordereau fractionné avec succès.",
        )


class BordereauLineViewSet(BaseViewSet):
    queryset = BordereauLine.objects.select_related(
        "bordereau", "feessheet__wording", "payment_plan", "payment"
    )
    serializer_class = BordereauLineSerializer

    def get_permissions(self):
        if self.action in ("destroy", "update", "partial_update"):
            return [IsFinanceService()]
        # list, retrieve, create → student_service + finance_service
        return [IsStudentOrFinance()]

    def get_queryset(self):
        qs = super().get_queryset()
        bordereau_id = self.request.query_params.get("bordereau_id")
        if bordereau_id:
            qs = qs.filter(bordereau_id=bordereau_id)
        return qs

    def perform_create(self, serializer):
        from django.db import transaction

        line = serializer.save()
        bordereau = line.bordereau

        # Numéro de ligne : compte les lignes existantes de ce bordereau
        line_number = BordereauLine.objects.filter(bordereau=bordereau).count()
        transaction_code = f"{bordereau.numero}/{line_number:02d}"

        # Inscription active de l'étudiant
        inscription = (
            bordereau.student.inscriptions.filter(
                regist_status__in=["Active", "Pending", "Complement"]
            )
            .order_by("-date_inscription")
            .first()
        )

        if inscription and line.payment_plan:
            with transaction.atomic():
                payment = Payment.objects.create(
                    paymentplan=line.payment_plan,
                    amount_paid=line.amount,
                    payment_date=bordereau.payment_date,
                    payment_method=bordereau.payment_method,
                    bank=bordereau.bank,
                    transaction_code=transaction_code,
                    inscription=inscription,
                    user=self.request.user,
                    payment_status="unverified",
                    description=f"Bordereau {bordereau.numero} — Ligne {line_number:02d}",
                )
                BordereauLine.objects.filter(pk=line.pk).update(payment=payment)
