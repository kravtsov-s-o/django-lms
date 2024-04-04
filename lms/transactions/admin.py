from django.contrib import admin
from .models import LessonStudentPrice, LessonTeacherPrice, LessonCompanyPrice

# Register your models here.
admin.site.register(LessonStudentPrice)
admin.site.register(LessonTeacherPrice)
admin.site.register(LessonCompanyPrice)