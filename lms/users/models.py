from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    SCHOOL_ROLE_CHOICES = (
        ('None', 'None'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    school_role = models.CharField(max_length=10, choices=SCHOOL_ROLE_CHOICES, default='None')
