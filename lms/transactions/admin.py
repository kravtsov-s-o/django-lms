from django.contrib import admin
from .models import TransactionType, StudentPayment, TeacherPayment, CompanyPayment
from modeltranslation.admin import TranslationAdmin
from django.utils.translation import gettext_lazy as _


# Register your models here.
@admin.register(TransactionType)
class TransactionTypeAdmin(TranslationAdmin):
    list_display = ['title', 'description', 'type', 'is_system']


@admin.register(TeacherPayment)
class TeacherPaymentAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'created_at', 'lesson', 'price']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(StudentPayment)
class StudentPaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'created_at', 'lesson', 'price', 'get_description']

    def get_description(self, obj):
        return obj.transaction_type.description

    get_description.short_description = _('Description')


@admin.register(CompanyPayment)
class CompanyPaymentAdmin(admin.ModelAdmin):
    list_display = ['company', 'created_at', 'lesson', 'price']
