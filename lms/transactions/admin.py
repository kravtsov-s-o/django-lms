from django.contrib import admin
from .models import StudentPayment, TeacherPayment, CompanyPayment


# Register your models here.
@admin.register(TeacherPayment)
class TeacherPaymentAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'created_at', 'lesson', 'price', 'description']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(StudentPayment)
class StudentPaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'created_at', 'lesson', 'price', 'description']


@admin.register(CompanyPayment)
class CompanyPaymentAdmin(admin.ModelAdmin):
    list_display = ['company', 'created_at', 'lesson', 'price', 'description']
