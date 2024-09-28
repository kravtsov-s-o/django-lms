from datetime import datetime

from django.db import models
from users.models import User
from settings.models import Currency, Language, Duration
from companies.models import Company
from django.utils.translation import gettext_lazy as _


# Create your models here.
class CommonFields(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, verbose_name=_('user'))
    language = models.ManyToManyField(Language, verbose_name=_('language'))
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('rate'))
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, verbose_name=_('currency'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('created at'))

    class Meta:
        abstract = True

    def __str__(self):
        if self.user.first_name == '' and self.user.last_name == '':
            return f'{self.user.username}'
        return f'{self.user.first_name} {self.user.last_name}'


class Teacher(CommonFields):
    about = models.TextField(blank=True, verbose_name=_('about'))

    class Meta:
        verbose_name = _('Teacher')
        verbose_name_plural = _('Teachers')


class Student(CommonFields):
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('company'))
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='teacher',
                                verbose_name=_('teacher'))
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('wallet'))

    class Meta:
        verbose_name = _('Student')
        verbose_name_plural = _('Students')


class Lesson(models.Model):
    LESSON_STATUSES = [
        ('planned', _('Planned')),
        ('conducted', _('Conducted')),
        ('missed', _('Missed')),
    ]

    date = models.DateField(default=datetime.now, null=False, verbose_name=_('date'))
    time = models.TimeField(null=False, verbose_name=_('time'))
    status = models.CharField(max_length=50, choices=LESSON_STATUSES, default='planned', verbose_name=_('status'))
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, verbose_name=_('teacher'))
    students = models.ManyToManyField(Student, verbose_name=_('students'))
    duration = models.ForeignKey(Duration, on_delete=models.SET_NULL, null=True, verbose_name=_('duration'))
    theme = models.CharField(max_length=255, null=False, verbose_name=_('theme'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('notes'))
    homework = models.TextField(blank=True, null=True, verbose_name=_('homework'))
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('price'))
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('currency'))

    def __str__(self):
        return self.theme

    class Meta:
        verbose_name = _('Lesson')
        verbose_name_plural = _('Lessons')


class StudentProgress(models.Model):
    date = models.DateTimeField(auto_now_add=True, verbose_name=_('date'))
    title = models.CharField(max_length=255, verbose_name=_('title'))
    description = models.TextField(blank=True, null=True, verbose_name=_('description'))
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name=_('student'))
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, verbose_name=_('teacher'))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Student Progress')
        verbose_name_plural = _('Student Progresses')
