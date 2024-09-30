from django.core.cache import cache
from .models import SiteInfo


def site_info(request):

    settings = cache.get('site_settings')
    if not settings:
        settings = SiteInfo.objects.first()
        cache.set('site_settings', settings, 60 * 60)

    return {
        'site_title': settings.title,
        'site_tagline': settings.tagline,
        'site_logo_icon': settings.logo_icon,
        'site_logo_text': settings.logo_text,
        'site_logo_full': settings.logo_full,
        'site_phone_1': settings.phone1 if settings.phone1 else None,
        'site_phone_2': settings.phone2 if settings.phone2 else None,
        'site_email': settings.email,
    }
