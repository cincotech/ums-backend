from datetime import timedelta

from django.utils import timezone

from .models import AuditLog, Module, UniversityProfile, UniversitySubscription


class UniversityProfileService:
    """Service for managing university profiles"""

    @staticmethod
    def create_profile(university, contact_email, contact_phone=None, website=None):
        """Create university profile"""
        profile, created = UniversityProfile.objects.get_or_create(
            university=university,
            defaults={
                "contact_email": contact_email,
                "contact_phone": contact_phone,
                "website": website,
            },
        )
        return profile

    @staticmethod
    def update_profile(university, **kwargs):
        """Update university profile"""
        profile = UniversityProfile.objects.get(university=university)

        allowed_fields = [
            "status",
            "contact_email",
            "contact_phone",
            "website",
            "description",
            "max_users",
            "max_storage_gb",
        ]

        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(profile, field, value)

        profile.save()
        return profile

    @staticmethod
    def get_profile(university):
        """Get university profile"""
        try:
            return UniversityProfile.objects.get(university=university)
        except UniversityProfile.DoesNotExist:
            return None


class ModuleService:
    """Service for managing system modules"""

    @staticmethod
    def create_module(name, description, code):
        """Create new module"""
        if Module.objects.filter(code=code).exists():
            raise ValueError(f"Module with code {code} already exists")

        module = Module.objects.create(name=name, description=description, code=code)
        return module

    @staticmethod
    def get_all_modules():
        """Get all active modules"""
        return Module.objects.filter(is_active=True)

    @staticmethod
    def get_module(module_id):
        """Get module by ID"""
        try:
            return Module.objects.get(id=module_id)
        except Module.DoesNotExist:
            return None


class SubscriptionService:
    """Service for managing university subscriptions"""

    @staticmethod
    def subscribe_university(
        university, module_id, start_date, end_date, created_by, is_trial=False
    ):
        """Subscribe university to module"""
        try:
            module = Module.objects.get(id=module_id)
        except Module.DoesNotExist:
            raise ValueError(f"Module {module_id} not found")

        # Check if already subscribed
        existing = UniversitySubscription.objects.filter(
            university=university, module=module
        ).first()

        if existing and existing.status == "active":
            raise ValueError(f"University already subscribed to {module.name}")

        # Create or update subscription
        subscription, created = UniversitySubscription.objects.update_or_create(
            university=university,
            module=module,
            defaults={
                "status": "active",
                "start_date": start_date,
                "end_date": end_date,
                "is_trial": is_trial,
                "created_by": created_by,
            },
        )

        # Log action
        AuditLog.objects.create(
            user=created_by,
            university=university,
            action="create",
            severity="info",
            entity_type="UniversitySubscription",
            entity_id=str(subscription.id),
            description=f"Subscribed to module: {module.name}",
            success=True,
        )

        return subscription

    @staticmethod
    def cancel_subscription(subscription_id, cancelled_by):
        """Cancel subscription"""
        try:
            subscription = UniversitySubscription.objects.get(id=subscription_id)
            subscription.status = "inactive"
            subscription.save()

            AuditLog.objects.create(
                user=cancelled_by,
                university=subscription.university,
                action="update",
                severity="info",
                entity_type="UniversitySubscription",
                entity_id=str(subscription.id),
                description=f"Cancelled subscription to: {subscription.module.name}",
                success=True,
            )

            return subscription
        except UniversitySubscription.DoesNotExist:
            raise ValueError("Subscription not found")

    @staticmethod
    def renew_subscription(subscription_id, new_end_date, renewed_by):
        """Renew subscription"""
        try:
            subscription = UniversitySubscription.objects.get(id=subscription_id)
            old_end_date = subscription.end_date
            subscription.end_date = new_end_date
            subscription.status = "active"
            subscription.save()

            AuditLog.objects.create(
                user=renewed_by,
                university=subscription.university,
                action="update",
                severity="info",
                entity_type="UniversitySubscription",
                entity_id=str(subscription.id),
                description=f"Renewed subscription to: {subscription.module.name}",
                changes={
                    "old_end_date": str(old_end_date),
                    "new_end_date": str(new_end_date),
                },
                success=True,
            )

            return subscription
        except UniversitySubscription.DoesNotExist:
            raise ValueError("Subscription not found")

    @staticmethod
    def get_university_subscriptions(university):
        """Get all subscriptions for university"""
        return UniversitySubscription.objects.filter(
            university=university
        ).select_related("module")

    @staticmethod
    def get_active_subscriptions(university):
        """Get active subscriptions for university"""
        return UniversitySubscription.objects.filter(
            university=university, status="active"
        ).select_related("module")

    @staticmethod
    def check_module_access(university, module_code):
        """Check if university has access to module"""
        return UniversitySubscription.objects.filter(
            university=university, module__code=module_code, status="active"
        ).exists()

    @staticmethod
    def get_expiring_subscriptions(days=30):
        """Get subscriptions expiring within days"""
        expiry_date = timezone.now().date() + timedelta(days=days)
        return UniversitySubscription.objects.filter(
            status="active",
            end_date__lte=expiry_date,
            end_date__gte=timezone.now().date(),
        ).select_related("university", "module")

    @staticmethod
    def get_expired_subscriptions():
        """Get expired subscriptions"""
        return UniversitySubscription.objects.filter(
            status="active", end_date__lt=timezone.now().date()
        ).select_related("university", "module")

    @staticmethod
    def auto_expire_subscriptions():
        """Auto-expire subscriptions that have passed end date"""
        expired = SubscriptionService.get_expired_subscriptions()
        count = 0
        for subscription in expired:
            subscription.status = "expired"
            subscription.save()
            count += 1
        return count
