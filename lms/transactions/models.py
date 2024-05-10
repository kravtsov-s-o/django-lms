from datetime import datetime

from django.db import models
from school.models import Lesson, Teacher, Student
from companies.models import Company


# Create your models here.
class TransactionBase(models.Model):
    created_at = models.DateField(default=datetime.now)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True


class StudentPayment(TransactionBase):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student.user.first_name} {self.student.user.last_name}"


class TeacherPayment(TransactionBase):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.teacher.user.first_name} {self.teacher.user.last_name}"


class CompanyPayment(TransactionBase):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.company.name
