from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from settings.models import Currency


# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=255, null=False, unique=True, db_index=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.IntegerField(validators=[
        MinValueValidator(0, "Discount cannot be less than 0."),
        MaxValueValidator(100, "Discount cannot be greater than 100."),
    ], default=0)

    def __str__(self):
        return f"{self.name}"




