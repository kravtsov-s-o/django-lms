from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class SchoolRole(models.TextChoices):
        NONE = 'None', _('None')
        TEACHER = 'teacher', _('Teacher')
        STUDENT = 'student', _('Student')

    school_role = models.CharField(
        max_length=10,
        verbose_name=_('School role'),
        choices=SchoolRole.choices,
        default=SchoolRole.NONE
    )
