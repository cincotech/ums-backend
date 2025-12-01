from django.urls import include, path

urlpatterns = [
    path(
        "dashboard/",
        include(
            "services.dependent_service.dashboard_module.dashboard_academic_app.urls"
        ),
    ),
    path(
        "dashboard/",
        include(
            "services.dependent_service.dashboard_module.dashboard_super_admin_app.urls"
        ),
    ),
    path(
        "dashboard/",
        include(
            "services.dependent_service.dashboard_module.dashboard_recteur_app.urls"
        ),
    ),
    path(
        "dashboard/",
        include(
            "services.dependent_service.dashboard_module.dashboard_quality_director_app.urls"
        ),
    ),
    path(
        "dashboard/",
        include(
            "services.dependent_service.dashboard_module.dashboard_student_services_app.urls"
        ),
    ),
    path(
        "dashboard/",
        include(
            "services.dependent_service.dashboard_module.dashboard_collection_agent_app.urls"
        ),
    ),
    path(
        "dashboard/",
        include(
            "services.dependent_service.dashboard_module.dashboard_student_app.urls"
        ),
    ),
    path(
        "dashboard/",
        include(
            "services.dependent_service.dashboard_module.dashboard_academic_secretary_app.urls"
        ),
    ),
    path(
        "dashboard/",
        include(
            "services.dependent_service.dashboard_module.dashboard_alumni_app.urls"
        ),
    ),
    path(
        "dashboard/admin/",
        include("services.dependent_service.dashboard_module.dashboard_admin_app.urls"),
    ),
    # path(
    #     "dashboard/doyen/",
    #     include("services.dependent_service.dashboard_module.dashboard_doyen_app.urls"),
    # ),
]
