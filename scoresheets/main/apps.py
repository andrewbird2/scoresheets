from django import apps
from django.utils.translation import gettext_lazy as _


class MainConfig(apps.AppConfig):
    name = "scoresheets.main"
    verbose_name = _("Main")

    def ready(self):
        try:
            import scoresheets.main.signals  # noqa: F401
        except ImportError:
            pass