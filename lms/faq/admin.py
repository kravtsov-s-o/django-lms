from django.contrib import admin
from .models import Category, Question
from modeltranslation.admin import TranslationAdmin


# Register your models here.
@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ['title']


@admin.register(Question)
class QuestionAdmin(TranslationAdmin):
    list_display = ['question', 'category']
    list_filter = ['category']
    search_fields = ['question']
