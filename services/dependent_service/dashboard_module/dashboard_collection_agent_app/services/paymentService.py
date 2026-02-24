import logging

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from ..models import Payment, PaymentInstallement, PaymentPlan

logger = logging.getLogger(__name__)


class PaymentService:
    """Service métier pour gérer la création, vérification et redistribution des paiements."""

    @classmethod
    def create_payment(
        cls,
        student,
        target_plan,
        amount,
        payment_method,
        bank=None,
        transaction_code=None,
    ):
        """Crée un paiement et redistribue automatiquement si nécessaire."""
        logger.info(f"\n{'='*80}")
        logger.info("🔵 CREATE_PAYMENT - Début")
        logger.info(f"Étudiant: {student.user.get_full_name()} ({student.matricule})")
        logger.info(f"Plan cible: {target_plan.description}")
        logger.info(f"Montant: {amount}")
        logger.info(f"Méthode: {payment_method}")
        logger.info(f"{'='*80}\n")

        remaining_amount = amount

        try:
            with transaction.atomic():
                # 🔹 0️⃣ Assurer que tous les installments précédents existent
                logger.info("📋 Étape 0: Création des installments précédents")
                cls._ensure_previous_installments(student, target_plan, student.user)

                # 1️⃣ Appliquer aux plans précédents non payés
                logger.info("\n💰 Étape 1: Distribution aux plans précédents")
                remaining_amount = cls._distribute_to_previous_plans(
                    student,
                    target_plan,
                    remaining_amount,
                    payment_method,
                    bank,
                    transaction_code,
                )
                logger.info(f"Montant restant après distribution: {remaining_amount}")

                # 2️⃣ Appliquer le reste sur le plan cible
                logger.info("\n🎯 Étape 2: Application au plan cible")
                cls._apply_to_target_plan(
                    student,
                    target_plan,
                    remaining_amount,
                    payment_method,
                    bank,
                    transaction_code,
                )

                logger.info("\n✅ CREATE_PAYMENT - Succès")
                logger.info(f"{'='*80}\n")
        except Exception as e:
            logger.error(f"\n❌ CREATE_PAYMENT - Erreur: {str(e)}")
            logger.error(f"{'='*80}\n")
            raise

    @classmethod
    def verify_payment(cls, payment, verified_by_user):
        """Vérifie un paiement et met à jour les installments"""
        logger.info(f"\n{'='*80}")
        logger.info("✅ VERIFY_PAYMENT - Début")
        logger.info(f"Payment ID: {payment.id}")
        logger.info(f"Montant: {payment.amount_paid}")
        logger.info(f"Vérifié par: {verified_by_user.get_full_name()}")
        logger.info(f"{'='*80}\n")

        if verified_by_user.role.name != "finance_service":
            logger.error("❌ Erreur: Seul le service financier peut valider")
            raise ValueError("Seul le service financier peut valider les paiements.")

        try:
            with transaction.atomic():
                payment.payment_status = "verified"
                payment.verified_by = verified_by_user
                payment.verified_at = timezone.now()
                payment.save()
                logger.info("✅ Paiement vérifié")

                # Redistribuer les surplus si besoin
                surplus = max(payment.amount_paid - payment.paymentplan.total_amount, 0)
                if surplus > 0:
                    logger.info(f"\n💸 Surplus détecté: {surplus}")
                    cls._handle_surplus(
                        payment.inscription.student,
                        payment.paymentplan,
                        surplus,
                        payment.payment_method,
                        payment.bank,
                        payment.transaction_code,
                    )
                else:
                    logger.info("✅ Pas de surplus")

                logger.info("\n✅ VERIFY_PAYMENT - Succès")
                logger.info(f"{'='*80}\n")
        except Exception as e:
            logger.error(f"\n❌ VERIFY_PAYMENT - Erreur: {str(e)}")
            logger.error(f"{'='*80}\n")
            raise

    @classmethod
    def unverify_payment(cls, payment, unverified_by_user):
        """Rejette un paiement vérifié et supprime les paiements redistribués automatiquement"""
        logger.info(f"\n{'='*80}")
        logger.info("❌ UNVERIFY_PAYMENT - Début")
        logger.info(f"Payment ID: {payment.id}")
        logger.info(f"Rejeté par: {unverified_by_user.get_full_name()}")
        logger.info(f"{'='*80}\n")

        if unverified_by_user.role.name != "finance_service":
            logger.error("❌ Erreur: Seul le service financier peut rejeter")
            raise ValueError("Seul le service financier peut rejeter les paiements.")

        if payment.payment_status != "verified":
            logger.error("❌ Erreur: Seuls les paiements vérifiés peuvent être rejetés")
            raise ValueError("Seuls les paiements vérifiés peuvent être rejetés.")

        student = payment.inscription.student

        try:
            with transaction.atomic():
                # 1️⃣ Identifier et supprimer tous les paiements redistribués automatiquement
                logger.info("🔍 Recherche des paiements automatiques...")
                auto_payments = Payment.objects.filter(
                    inscription__student=student,
                    payment_status="verified",
                    description__icontains="Redistribution automatique",
                ) | Payment.objects.filter(
                    inscription__student=student,
                    payment_status="verified",
                    description__icontains="Surplus",
                )

                count = auto_payments.count()
                logger.info(f"🗑️ Suppression de {count} paiements automatiques")
                auto_payments.delete()

                # 2️⃣ Changer le statut du paiement original en "unverified"
                logger.info("🔄 Changement du statut en 'unverified'")
                payment.payment_status = "unverified"
                payment.verified_by = None
                payment.verified_at = None
                payment.save()

                # 3️⃣ Recalculer TOUS les installments de l'étudiant
                logger.info("📊 Recalcul des installments...")
                installments = PaymentInstallement.objects.filter(
                    student=student
                ).order_by("payment_plan__start_date")
                for installment in installments:
                    total_verified = (
                        Payment.objects.filter(
                            paymentplan=installment.payment_plan,
                            payment_status="verified",
                            inscription__student=student,
                        ).aggregate(total=Sum("amount_paid"))["total"]
                        or 0
                    )
                    installment.paid_amount = total_verified
                    installment.save()
                    logger.info(
                        f"  - {installment.payment_plan.description}: {total_verified}"
                    )

                logger.info("\n✅ UNVERIFY_PAYMENT - Succès")
                logger.info(f"{'='*80}\n")
        except Exception as e:
            logger.error(f"\n❌ UNVERIFY_PAYMENT - Erreur: {str(e)}")
            logger.error(f"{'='*80}\n")
            raise

    @classmethod
    def reverse_payment(cls, payment):
        """Supprime complètement un paiement (pour erreurs graves)"""
        student = payment.inscription.student

        with transaction.atomic():
            payment.delete()

            # Recalculer tous les installments affectés
            installments = PaymentInstallement.objects.filter(student=student).order_by(
                "payment_plan__start_date"
            )
            for installment in installments:
                total_verified = (
                    Payment.objects.filter(
                        paymentplan=installment.payment_plan,
                        payment_status="verified",
                        inscription__student=student,
                    ).aggregate(total=Sum("amount_paid"))["total"]
                    or 0
                )
                installment.paid_amount = total_verified
                installment.save()

    # --- Méthodes internes ---

    @classmethod
    def _ensure_previous_installments(cls, student, target_plan, user):
        """Crée tous les installments pour les plans précédents non encore créés."""
        previous_plans = PaymentPlan.objects.filter(
            start_date__lt=target_plan.start_date, status="active"
        ).order_by("start_date")

        for plan in previous_plans:
            PaymentInstallement.objects.get_or_create(
                student=student,
                payment_plan=plan,
                defaults={
                    "amount": plan.total_amount,
                    "due_date": plan.end_date,
                    "created_by": user,
                },
            )

    @classmethod
    def _distribute_to_previous_plans(
        cls, student, target_plan, amount, payment_method, bank, transaction_code
    ):
        """Redistribue l'argent sur les plans précédents impayés"""
        logger.info("  🔍 Recherche des plans précédents impayés...")
        remaining_amount = amount
        previous_installments = PaymentInstallement.objects.filter(
            student=student,
            payment_plan__start_date__lt=target_plan.start_date,
            status__in=["pending", "overdue"],
        ).order_by("payment_plan__start_date")

        logger.info(
            f"  📊 {previous_installments.count()} plan(s) précédent(s) trouvé(s)"
        )

        for installment in previous_installments:
            remaining_capacity = installment.amount - installment.paid_amount
            if remaining_capacity <= 0:
                logger.info(f"  ⏭️ {installment.payment_plan.description} - Déjà payé")
                continue

            to_pay = min(remaining_amount, remaining_capacity)
            logger.info(
                f"  💵 {installment.payment_plan.description} - Paiement de {to_pay}"
            )

            payment = Payment(
                paymentplan=installment.payment_plan,
                amount_paid=to_pay,
                payment_method=payment_method,
                bank=bank,
                transaction_code=transaction_code,
                inscription=student.inscriptions.first(),
                user=student.user,
                description=f"Redistribution automatique sur plan {installment.payment_plan.description}",
                payment_status="verified",
            )
            payment.save(_skip_surplus_handling=True)
            installment.paid_amount += to_pay
            installment.save()
            logger.info(f"  ✅ Payment créé: {payment.id}")

            remaining_amount -= to_pay
            if remaining_amount <= 0:
                logger.info("  🚫 Montant épuisé")
                break

        return remaining_amount

    @classmethod
    def _apply_to_target_plan(
        cls, student, target_plan, amount, payment_method, bank, transaction_code
    ):
        """Applique le paiement au plan cible et gère le surplus"""
        if amount <= 0:
            return

        with transaction.atomic():
            payment = Payment(
                paymentplan=target_plan,
                amount_paid=amount,
                payment_method=payment_method,
                bank=bank,
                transaction_code=transaction_code,
                inscription=student.inscriptions.first(),
                user=student.user,
                description=f"Paiement principal sur plan {target_plan.description}",
                payment_status="verified",
            )
            payment.save(_skip_surplus_handling=True)

            installment, _ = PaymentInstallement.objects.get_or_create(
                student=student,
                payment_plan=target_plan,
                defaults={
                    "amount": target_plan.total_amount,
                    "due_date": target_plan.end_date,
                    "created_by": student.user,
                },
            )

            total_verified = (
                Payment.objects.filter(
                    paymentplan=target_plan,
                    payment_status="verified",
                    inscription__student=student,
                ).aggregate(total=Sum("amount_paid"))["total"]
                or 0
            )

            installment.paid_amount = min(total_verified, installment.amount)
            installment.save()

            surplus = max(total_verified - installment.amount, 0)
            if surplus > 0:
                cls._handle_surplus(
                    student,
                    target_plan,
                    surplus,
                    payment_method,
                    bank,
                    transaction_code,
                )

    @classmethod
    def _handle_surplus(
        cls, student, current_plan, surplus, payment_method, bank, transaction_code
    ):
        """Redistribue le surplus hiérarchiquement: précédents puis suivants jusqu'à épuisement"""
        logger.info("\n  💸 HANDLE_SURPLUS - Début")
        logger.info(f"  Surplus: {surplus}")
        logger.info(f"  Plan actuel: {current_plan.description}")

        remaining_surplus = surplus
        last_next_plan = None

        # OPTIMISATION: Récupérer tous les plans et installments en une seule requête
        student_plans = list(
            PaymentPlan.get_plans_for_student(student)
            .select_related("feessheet")
            .order_by("start_date")
        )

        # Précharger tous les installments existants
        existing_installments = {
            inst.payment_plan_id: inst
            for inst in PaymentInstallement.objects.filter(
                student=student, payment_plan__in=student_plans
            ).select_related("payment_plan")
        }

        # Récupérer l'inscription une seule fois
        student_inscription = student.inscriptions.first()

        try:
            iteration = 0
            max_iterations = len(student_plans) * 2  # Sécurité contre boucle infinie

            while remaining_surplus > 0 and iteration < max_iterations:
                iteration += 1
                logger.info(
                    f"\n  🔄 Itération {iteration} - Surplus restant: {remaining_surplus}"
                )

                # Chercher le plan précédent NON COMPLET
                previous_plan = None
                for plan in reversed(student_plans):
                    if (
                        plan.start_date < current_plan.start_date
                        and plan.status == "active"
                    ):
                        # Vérifier si le plan a encore de la capacité
                        if plan.id in existing_installments:
                            inst = existing_installments[plan.id]
                            if inst.paid_amount < inst.amount:
                                previous_plan = plan
                                break
                        else:
                            previous_plan = plan
                            break

                if previous_plan:
                    logger.info(
                        f"  ⬅️ Plan précédent trouvé: {previous_plan.description}"
                    )
                    target_plan = previous_plan
                    is_next_plan = False
                else:
                    # Chercher le plan suivant NON COMPLET
                    next_plan = None
                    for plan in student_plans:
                        if (
                            plan.start_date > current_plan.start_date
                            and plan.status == "active"
                        ):
                            # Vérifier si le plan a encore de la capacité
                            if plan.id in existing_installments:
                                inst = existing_installments[plan.id]
                                if inst.paid_amount < inst.amount:
                                    next_plan = plan
                                    break
                            else:
                                next_plan = plan
                                break

                    if next_plan:
                        logger.info(f"  ➡️ Plan suivant trouvé: {next_plan.description}")
                        target_plan = next_plan
                        last_next_plan = next_plan
                        is_next_plan = True
                    else:
                        # TOUS les plans sont complets - Ajouter le surplus au dernier plan suivant
                        final_plan = last_next_plan if last_next_plan else current_plan
                        logger.info(
                            f"  🎯 Tous les plans complets - Ajout du surplus au plan {final_plan.description}"
                        )

                        if final_plan.id in existing_installments:
                            installment = existing_installments[final_plan.id]
                        else:
                            installment = PaymentInstallement(
                                student=student,
                                payment_plan=final_plan,
                                amount=final_plan.total_amount,
                                due_date=final_plan.end_date,
                                created_by=student.user,
                            )

                        installment.paid_amount += remaining_surplus
                        installment.save()

                        payment = Payment(
                            paymentplan=final_plan,
                            amount_paid=remaining_surplus,
                            payment_method=payment_method,
                            bank=bank,
                            transaction_code=transaction_code,
                            inscription=student_inscription,
                            user=student.user,
                            description=f"Surplus final du plan {current_plan.description}",
                            payment_status="verified",
                        )
                        payment.save(_skip_surplus_handling=True)
                        logger.info(
                            f"  ✅ Surplus final créé: {payment.id} - Montant: {remaining_surplus}"
                        )
                        break

                # Traiter le plan cible
                if target_plan.id in existing_installments:
                    target_installment = existing_installments[target_plan.id]
                else:
                    target_installment = PaymentInstallement(
                        student=student,
                        payment_plan=target_plan,
                        amount=target_plan.total_amount,
                        due_date=target_plan.end_date,
                        created_by=student.user,
                    )
                    existing_installments[target_plan.id] = target_installment

                remaining_capacity = (
                    target_installment.amount - target_installment.paid_amount
                )
                transfer_amount = min(remaining_surplus, remaining_capacity)

                logger.info(
                    f"  💵 Transfert de {transfer_amount} vers {target_plan.description}"
                )

                payment = Payment(
                    paymentplan=target_plan,
                    amount_paid=transfer_amount,
                    payment_method=payment_method,
                    bank=bank,
                    transaction_code=transaction_code,
                    inscription=student_inscription,
                    user=student.user,
                    description=f"Surplus transféré du plan {current_plan.description}",
                    payment_status="verified",
                )
                payment.save(_skip_surplus_handling=True)
                logger.info(f"  ✅ Payment surplus créé: {payment.id}")

                target_installment.paid_amount = min(
                    target_installment.paid_amount + transfer_amount,
                    target_installment.amount,
                )
                target_installment.save()

                remaining_surplus -= transfer_amount
                current_plan = target_plan
                if is_next_plan:
                    last_next_plan = target_plan

            logger.info("\n  ✅ HANDLE_SURPLUS - Terminé")
        except Exception as e:
            logger.error(f"\n  ❌ HANDLE_SURPLUS - Erreur: {str(e)}")
            raise
