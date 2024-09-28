from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=255, null=False, blank=False, verbose_name=_('title'))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')


class Question(models.Model):
    question = models.CharField(max_length=255, null=False, blank=False, verbose_name=_('question'))
    answer = models.TextField(null=False, blank=False, verbose_name=_('answer'))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name=_('category'))

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')
