from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = _('users and groups')

    def ready(self):
        import users.signals
        from django.contrib.auth.models import Group
        Group._meta.app_label = 'users'
