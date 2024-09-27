from django.db import models
from django.urls import reverse

from users.models import User

from django_ckeditor_5.fields import CKEditor5Field


# Create your models here.
class Page(models.Model):
    PAGE_STATUSES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=255, null=False, blank=False)
    slug = models.SlugField(max_length=255, unique=True, null=False, blank=False)
    content = CKEditor5Field(null=False, blank=False)
    status = models.CharField(max_length=50, choices=PAGE_STATUSES, default='draft')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('pages:page', kwargs={'slug': self.slug})
