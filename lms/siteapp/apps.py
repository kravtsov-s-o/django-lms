from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SiteappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'siteapp'
    verbose_name = _('site')

    def ready(self):
        # Импортируем сигналы при готовности приложения
        import siteapp.signals
