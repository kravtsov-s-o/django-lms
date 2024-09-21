from django.contrib import admin
from .models import Category, Question


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question', 'category']
    list_filter = ['category']
    search_fields = ['question']
