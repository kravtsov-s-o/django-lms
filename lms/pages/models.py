from django.db import models

from users.models import User

from ckeditor.fields import RichTextField


# Create your models here.
class Page(models.Model):
    PAGE_STATUSES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=255, null=False, blank=False)
    slug = models.SlugField(max_length=255, unique=True, null=False, blank=False)
    content = RichTextField(null=False, blank=False)
    status = models.CharField(max_length=50, choices=PAGE_STATUSES, default='draft')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
