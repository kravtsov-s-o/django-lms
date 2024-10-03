from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import SiteInfo

# Сброс кэша при сохранении или изменении объекта SiteInfo
@receiver(post_save, sender=SiteInfo)
def clear_cache_on_save(sender, instance, **kwargs):
    cache.delete('site_settings')