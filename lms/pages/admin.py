from django.contrib import admin

from .models import Page
from .forms import PageForm


# Register your models here.
@admin.register(Page)
class PageAdmin(admin.ModelAdmin):

    form = PageForm

    search_fields = ['title', 'content']
    list_display = ['title', 'author', 'status']
    list_filter = ['status', 'author']
    readonly_fields = ['author', 'created_at', 'updated_at']

    class Media:
        js = ('js/admin/admin_slug_generator.js',)

    def save_model(self, request, obj, form, change):
        if not change or not obj.author:
            # Если это создание объекта или поле author пустое, заполняем автором текущего пользователя
            obj.author = request.user
        obj.save()
