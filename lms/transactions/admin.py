from django.contrib import admin
from .models import CategoryPrice, Price, TransactionType, StudentPayment, TeacherPayment, CompanyPayment
from modeltranslation.admin import TranslationAdmin
from django.utils.translation import gettext_lazy as _


# Register your models here.
@admin.register(CategoryPrice)
class CategoryPriceAdmin(admin.ModelAdmin):
    list_display = ['title']


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'price', 'currency', 'period_type', 'period_duration', 'discount',
                    'discount_date_end', 'category']
    list_filter = ['currency', 'category', 'period_type']
    readonly_fields = ['period_type', 'period_duration']


@admin.register(TransactionType)
class TransactionTypeAdmin(TranslationAdmin):
    list_display = ['title', 'description', 'type', 'is_system']
    readonly_fields = ['is_system']

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_system:
            return False
        return super().has_delete_permission(request, obj)


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
