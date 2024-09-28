from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Language(models.Model):
    name = models.CharField(max_length=255, null=False, unique=True, verbose_name=_('name'))

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Language')
        verbose_name_plural = _('Languages')


class Duration(models.Model):
    time = models.IntegerField(null=False, unique=True, verbose_name=_('time'))

    def __str__(self):
        return f"{self.time} min"

    class Meta:
        verbose_name = _('Duration')
        verbose_name_plural = _('Durations')


class Currency(models.Model):
    name = models.CharField(max_length=3, unique=True, null=False, verbose_name=_('name'))
    symbol = models.CharField(max_length=3, null=True, blank=True, verbose_name=_('symbol'))
    exchange = models.DecimalField(max_digits=10, decimal_places=5, null=False, verbose_name=_('exchange'))
    default = models.BooleanField(default=False, verbose_name=_('default'))

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Currency')
        verbose_name_plural = _('Currencies')
