from import_export import resources

from .models import Profile


class ProfileResource(resources.ModelResource):
    class Meta:
        model = Profile
        fields = ("id", "user__email", "position", "start_date", "end_date")
