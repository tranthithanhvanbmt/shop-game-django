from django.db.utils import DatabaseError
from django.shortcuts import render

from shop_game.core.models import SiteSetting


class MaintenanceModeMiddleware:
    """Show a maintenance page when SiteSetting.maintenance_mode is enabled."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path or ""

        # Always allow admin and static/media assets so operators can recover the site.
        bypass_prefixes = (
            "/quan-ly-bi-mat/",
            "/static/",
            "/media/",
            "/i18n/",
        )
        if path.startswith(bypass_prefixes):
            return self.get_response(request)

        try:
            setting = SiteSetting.objects.only("maintenance_mode", "site_name").first()
        except (DatabaseError, Exception):
            setting = None

        is_maintenance = bool(setting and setting.maintenance_mode)
        is_admin_user = bool(
            request.user.is_authenticated
            and (request.user.is_staff or request.user.is_superuser)
        )

        if is_maintenance and not is_admin_user:
            response = render(
                request,
                "maintenance.html",
                {"site_setting": setting},
                status=503,
            )
            response["Retry-After"] = "600"
            return response

        return self.get_response(request)
