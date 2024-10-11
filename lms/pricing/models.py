from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


# Create your models here.
class CategoryPlan(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('title'))

    def __str__(self):
        return self.title


class Plan(models.Model):
    class Periods(models.TextChoices):
        HOUR = 'hour', _('Hour')
        # MONTH = 'month', _('Month')

    category = models.ForeignKey(CategoryPlan, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255, null=False, blank=False, verbose_name=_('title'))
    description = models.CharField(max_length=255, null=False, blank=False, verbose_name=_('description'))
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('price'))
    currency = models.ForeignKey('settings.Currency', on_delete=models.SET_NULL, null=True, verbose_name=_('currency'))
    period_type = models.CharField(max_length=50, choices=Periods.choices, default=Periods.HOUR,
                                   verbose_name=_('period type'))
    period_duration = models.IntegerField(default=1, validators=[MinValueValidator(1, _("Can't be less 1"))],
                                          verbose_name=_('period duration'))
    discount = models.IntegerField(validators=[
        MinValueValidator(0, _("Discount can't be less than 0.")),
        MaxValueValidator(100, _("Discount can't be greater than 100.")),
    ], default=0)
    discount_date_end = models.DateField(null=True, blank=True, default=None, verbose_name=_("discount date end"))

    def __str__(self):
        return f"{self.title} - {self.price} {self.currency.symbol}"
