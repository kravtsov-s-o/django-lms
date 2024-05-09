from django.contrib import admin
from .models import StudentPayment, TeacherPayment, CompanyPayment

# Register your models here.
@admin.register(TeacherPayment)
class TeacherPaymentAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'lesson', 'price', 'description']
@admin.register(StudentPayment)
class StudentPaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'lesson', 'price', 'description']
@admin.register(CompanyPayment)
class CompanyPaymentAdmin(admin.ModelAdmin):
    list_display = ['company', 'lesson', 'price', 'description']
