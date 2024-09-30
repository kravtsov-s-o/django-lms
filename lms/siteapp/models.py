from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class SiteInfo(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('title'))
    tagline = models.CharField(max_length=255, verbose_name=_('tagline'), blank=True, null=True)
    logo_icon = models.ImageField(upload_to='static/img/', verbose_name=_('logo_icon'), blank=True, null=True)
    logo_text = models.ImageField(upload_to='static/img/', verbose_name=_('logo_text'), blank=True, null=True)
    logo_full = models.ImageField(upload_to='static/img/', verbose_name=_('logo_full'), blank=True, null=True)
    phone1 = models.CharField(max_length=255, verbose_name=_('phone'), blank=True, null=True)
    phone2 = models.CharField(max_length=255, verbose_name=_('phone'), blank=True, null=True)
    email = models.EmailField(verbose_name=_('email'), blank=True, null=True)

    class Meta:
        verbose_name = _('Site')
        verbose_name_plural = _('Sites')

    def __str__(self):
        return self.title
