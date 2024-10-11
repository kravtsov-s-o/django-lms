from django.utils import timezone
from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class CommonFields(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, null=True, verbose_name=_('user'))
    language = models.ManyToManyField('settings.Language', verbose_name=_('language'))
    price_plan = models.ForeignKey('pricing.Plan', on_delete=models.SET_NULL, null=True, verbose_name=_('price'))
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
    company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('company'))
    teacher = models.ForeignKey('school.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='teacher',
                                verbose_name=_('teacher'))
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('wallet'))

    class Meta:
        verbose_name = _('Student')
        verbose_name_plural = _('Students')


class Lesson(models.Model):
    class LessonStatus(models.TextChoices):
        PLANNED = 'planned', _('Planned')
        CONDUCTED = 'conducted', _('Conducted')
        MISSED = 'missed', _('Missed')

    date = models.DateField(default=timezone.now, null=False, verbose_name=_('date'))
    time = models.TimeField(null=False, verbose_name=_('time'))
    status = models.CharField(max_length=50, choices=LessonStatus.choices, default=LessonStatus.PLANNED, verbose_name=_('status'))
    teacher = models.ForeignKey('school.Teacher', on_delete=models.SET_NULL, null=True, verbose_name=_('teacher'))
    students = models.ManyToManyField('school.Student', verbose_name=_('students'))
    duration = models.ForeignKey('settings.Duration', on_delete=models.SET_NULL, null=True, verbose_name=_('duration'))
    theme = models.CharField(max_length=255, null=False, verbose_name=_('theme'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('notes'))
    homework = models.TextField(blank=True, null=True, verbose_name=_('homework'))
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('price'))
    currency = models.ForeignKey('settings.Currency', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('currency'))

    def __str__(self):
        return self.theme

    class Meta:
        verbose_name = _('Lesson')
        verbose_name_plural = _('Lessons')


class StudentProgress(models.Model):
    date = models.DateTimeField(auto_now_add=True, verbose_name=_('date'))
    title = models.CharField(max_length=255, verbose_name=_('title'))
    description = models.TextField(blank=True, null=True, verbose_name=_('description'))
    student = models.ForeignKey('school.Student', on_delete=models.CASCADE, verbose_name=_('student'))
    teacher = models.ForeignKey('school.Teacher', on_delete=models.SET_NULL, null=True, verbose_name=_('teacher'))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Student Progress')
        verbose_name_plural = _('Student Progresses')
