from django.db import models
from django.urls import reverse

from users.models import User

from django_ckeditor_5.fields import CKEditor5Field
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Page(models.Model):
    class PageStatuses(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        PUBLISHED = 'published', _('Published')

    title = models.CharField(max_length=255, null=False, blank=False, verbose_name=_('title'))
    slug = models.SlugField(max_length=255, unique=True, null=False, blank=False, verbose_name=_('slug'))
    content = models.TextField(null=False, blank=False, verbose_name=_('content'))
    status = models.CharField(max_length=50, choices=PageStatuses.choices, default=PageStatuses.DRAFT,
                              verbose_name=_('status'))
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_('author'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('updated at'))

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('pages:page', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = _('page')
        verbose_name_plural = _('pages')
