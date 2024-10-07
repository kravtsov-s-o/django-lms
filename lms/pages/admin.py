from django.contrib import admin

from .models import Page
from .forms import PageForm
from modeltranslation.admin import TranslationAdmin


# Register your models here.
@admin.register(Page)
class PageAdmin(TranslationAdmin):

    form = PageForm

    search_fields = ['title', 'content']
    list_display = ['title', 'slug', 'author', 'status']
    list_filter = ['status', 'author']
    readonly_fields = ['author', 'created_at', 'updated_at']

    prepopulated_fields = {'slug': ('title',)}

    def save_model(self, request, obj, form, change):
        if not change or not obj.author:
            obj.author = request.user
        obj.save()
