from django.core.cache import cache
from .models import SiteInfo
from users.models import User
from school.models import Lesson
from transactions.models import TransactionType, Price
from settings.models import Duration, Currency

DAILY_CACHE_TIME = 24 * 60 * 60  # 24 hours


def site_info(request):
    settings = cache.get('site_settings')
    if not settings:
        settings = SiteInfo.objects.first()
        cache.set('site_settings', settings, DAILY_CACHE_TIME)

    return {
        'site_title': settings.title,
        'site_tagline': settings.tagline,
        'site_logo_icon': settings.logo_icon if settings.logo_icon else '',
        'site_logo_text': settings.logo_text if settings.logo_text else '',
        'site_logo_full': settings.logo_full if settings.logo_full else '',
        'site_phone_1': settings.phone1 if settings.phone1 else None,
        'site_phone_2': settings.phone2 if settings.phone2 else None,
        'site_email': settings.email,
    }


def global_constants(request):
    currency_cache = cache.get('currency_cache')
    if not currency_cache:
        currency_cache = Currency.objects.all()
        cache.set('currency_cache', currency_cache, DAILY_CACHE_TIME)

    duration_cache = cache.get('duration_cache')
    if not duration_cache:
        duration_cache = Duration.objects.all().order_by('time')
        cache.set('duration_cache', duration_cache, DAILY_CACHE_TIME)

    return {
        'SCHOOL_ROLES': User.SchoolRole,
        'LESSON_STATUSES': Lesson.LessonStatus,
        'TRANSACTION_TYPES': TransactionType.TransactionTypes,
        'PRICE_PLAN_PERIODS': Price.Periods,
        'CURRENCIES': currency_cache,
        'DURATIONS': duration_cache,
    }
