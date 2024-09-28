from datetime import datetime

from django.db import models
from django.db.models import Sum, Case, When, IntegerField, Value
from django.db.models.functions import TruncMonth
from school.models import Lesson, Teacher, Student
from companies.models import Company
from django.utils.translation import gettext_lazy as _



# Create your models here.
class TransactionBase(models.Model):
    created_at = models.DateField(default=datetime.now, verbose_name=_('created at'))
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('lesson'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('price'))
    description = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('description'))

    class Meta:
        abstract = True


class StudentPayment(TransactionBase):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name=_('student'))
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.lesson:
            self.student.wallet += self.price
            self.student.save()

    def __str__(self):
        return f"{self.student.user.first_name} {self.student.user.last_name}"

    class Meta:
        verbose_name = _('Student Payment')
        verbose_name_plural = _('Students Payment')


class TeacherPaymentManager(models.Manager):
    def get_half_month_summaries(self, teacher, year):
        # Фильтруем данные за указанный год
        qs = self.filter(teacher=teacher, created_at__year=year)

        # Разбиваем на первую и вторую половину месяца
        half_month_aggregates = qs.annotate(
            half_month=Case(
                When(created_at__day__lte=15, then=Value(1)),
                When(created_at__day__gte=16, then=Value(2)),
                output_field=IntegerField(),
            ),
            month=TruncMonth('created_at')
        ).values('month', 'half_month').annotate(
            total_price=Sum('price')
        ).order_by('month', 'half_month')

        return half_month_aggregates


class TeacherPayment(TransactionBase):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name=_('teacher'))

    objects = TeacherPaymentManager()

    def __str__(self):
        return f"{self.teacher.user.first_name} {self.teacher.user.last_name}"

    class Meta:
        verbose_name = _('Teacher Payment')
        verbose_name_plural = _('Teachers Payment')


class CompanyPayment(TransactionBase):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name=_('company'))

    def save(self, *args, **kwargs):
        # Сначала вызываем метод save родительского класса
        super().save(*args, **kwargs)

        # Обновляем баланс ученика только если урок не указан
        if not self.lesson:
            self.company.wallet += self.price
            self.company.save()

    def __str__(self):
        return self.company.name

    class Meta:
        verbose_name = _('Company Payment')
        verbose_name_plural = _('Companies Payment')
