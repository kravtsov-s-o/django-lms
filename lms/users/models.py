from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    SCHOOL_ROLE_CHOICES = (
        ('None', _('None')),
        ('teacher', _('Teacher')),
        ('student', _('Student')),
    )

    school_role = models.CharField(max_length=10, verbose_name=_('School role'), choices=SCHOOL_ROLE_CHOICES, default='None')
