"""
Script pour forcer le recalcul et le transfert des surplus existants
Exécuter avec: python manage.py shell < fix_surplus.py
"""

from services.dependent_service.dashboard_module.dashboard_collection_agent_app.models import (
    Payment,
    PaymentInstallement,
)


def fix_surplus_for_payment(payment_id):
    """Force le recalcul du surplus pour un paiement spécifique"""
    try:
        payment = Payment.objects.get(id=payment_id)

        if payment.payment_status != "verified":
            print(f"❌ Le paiement {payment_id} n'est pas vérifié")
            return

        student = payment.inscription.student
        print(f"✅ Traitement du paiement {payment_id} pour {student.matricule}")

        # Recalculer le PaymentInstallement
        installment = PaymentInstallement.objects.filter(
            payment_plan=payment.paymentplan, student=student
        ).first()

        if not installment:
            print("❌ Aucun PaymentInstallement trouvé")
            return

        print(f"📊 Plan actuel: {payment.paymentplan.description}")
        print(f"   Montant requis: {installment.amount}")
        print(f"   Montant payé: {installment.paid_amount}")

        if installment.paid_amount > installment.amount:
            surplus = installment.paid_amount - installment.amount
            print(f"💰 Surplus détecté: {surplus}")

            # Forcer le transfert du surplus
            payment._handle_payment_surplus(student, surplus)
            print("✅ Surplus transféré avec succès")
        else:
            print("ℹ️  Pas de surplus à transférer")

    except Payment.DoesNotExist:
        print(f"❌ Paiement {payment_id} non trouvé")
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback

        traceback.print_exc()


def fix_all_surplus():
    """Recalcule tous les surplus pour tous les paiements vérifiés"""
    print("🔄 Recherche de tous les surplus à transférer...")

    # Trouver tous les PaymentInstallement avec surplus
    installments_with_surplus = PaymentInstallement.objects.filter(
        status="paid"
    ).select_related("payment_plan", "student")

    for installment in installments_with_surplus:
        if installment.paid_amount > installment.amount:
            surplus = installment.paid_amount - installment.amount
            print(f"\n💰 Surplus trouvé pour {installment.student.matricule}")
            print(f"   Plan: {installment.payment_plan.description}")
            print(f"   Surplus: {surplus}")

            # Trouver le dernier paiement vérifié pour ce plan
            last_payment = (
                Payment.objects.filter(
                    paymentplan=installment.payment_plan,
                    inscription__student=installment.student,
                    payment_status="verified",
                )
                .order_by("-verified_at")
                .first()
            )

            if last_payment:
                print(f"   Transfert via paiement: {last_payment.id}")
                last_payment._handle_payment_surplus(installment.student, surplus)
                print("   ✅ Surplus transféré")


# Exemple d'utilisation:
if __name__ == "__main__":
    # Pour un paiement spécifique
    payment_id = "ef4a659a-e9ab-4674-add9-bbcb9b053ce7"
    print(f"🚀 Traitement du paiement {payment_id}\n")
    fix_surplus_for_payment(payment_id)

    # Ou pour tous les surplus
    # print("\n🚀 Traitement de tous les surplus\n")
    # fix_all_surplus()
