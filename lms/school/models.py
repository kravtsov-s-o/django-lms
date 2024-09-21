from datetime import datetime

from django.db import models
from users.models import User
from settings.models import Currency, Language, Duration
from companies.models import Company


# Create your models here.
class CommonFields(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    language = models.ManyToManyField(Language)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        if self.user.first_name == '' and self.user.last_name == '':
            return f'{self.user.username}'
        return f'{self.user.first_name} {self.user.last_name}'


class Teacher(CommonFields):
    about = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'


class Student(CommonFields):
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='teacher')
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'


class Lesson(models.Model):
    LESSON_STATUSES = [
        ('planned', 'Planned'),
        ('сonducted', 'Conducted'),
        ('missed', 'Missed'),
    ]

    date = models.DateField(default=datetime.now, null=False)
    time = models.TimeField(default=datetime.now, null=False)
    status = models.CharField(max_length=50,  choices=LESSON_STATUSES, default='planned')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    students = models.ManyToManyField(Student)
    duration = models.ForeignKey(Duration, on_delete=models.SET_NULL, null=True)
    theme = models.CharField(max_length=255, null=False)
    notes = models.TextField(blank=True, null=True)
    homework = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.theme


class StudentProgress(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title

