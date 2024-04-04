from django.db import models
from school.models import Lesson, Teacher, Student
from companies.models import Company


# Create your models here.
class LessonPrice(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        abstract = True


class LessonStudentPrice(LessonPrice):
    students = models.ForeignKey(Student, on_delete=models.CASCADE)

    def __str__(self):
        return self.students


class LessonTeacherPrice(LessonPrice):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    def __str__(self):
        return self.teacher


class LessonCompanyPrice(LessonPrice):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.company
