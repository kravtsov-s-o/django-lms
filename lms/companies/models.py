from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=255, null=False, unique=True, db_index=True, verbose_name=_('name'))
    price_plan = models.ForeignKey('transactions.Price', on_delete=models.SET_NULL, null=True, verbose_name=_('price'))
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('wallet'))
    discount = models.IntegerField(validators=[
        MinValueValidator(0, _("Discount can't be less than 0.")),
        MaxValueValidator(100, _("Discount can't be greater than 100.")),
    ], default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')




