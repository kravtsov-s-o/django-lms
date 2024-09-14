from django.db import models


# Create your models here.
class Language(models.Model):
    name = models.CharField(max_length=255, null=False, unique=True)

    def __str__(self):
        return f"{self.name}"


class Duration(models.Model):
    time = models.IntegerField(null=False, unique=True)

    def __str__(self):
        return f"{self.time} min"


class Currency(models.Model):
    name = models.CharField(max_length=3, unique=True, null=False)
    symbol = models.CharField(max_length=3, null=True, blank=True)
    exchange = models.DecimalField(max_digits=10, decimal_places=5, null=False)
    default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"
