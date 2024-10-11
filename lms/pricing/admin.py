from django.contrib import admin
from .models import Plan, CategoryPlan
from modeltranslation.admin import TranslationAdmin
from django.utils.translation import gettext_lazy as _


# Register your models here.
@admin.register(CategoryPlan)
class CategoryPlanAdmin(admin.ModelAdmin):
    list_display = ['title']


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'price', 'currency', 'period_type', 'period_duration', 'discount',
                    'discount_date_end', 'category']
    list_filter = ['currency', 'category', 'period_type']
    readonly_fields = ['period_type', 'period_duration']
