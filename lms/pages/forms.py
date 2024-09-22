from django import forms
from django.utils.text import slugify

from .models import Page


class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = '__all__'

    def save(self, commit=True):
        # Сначала выполняем стандартное сохранение формы
        instance = super(PageForm, self).save(commit=False)

        # Если slug пустой, генерируем его из title
        if not instance.slug:
            instance.slug = slugify(instance.title)

        # Если нужно сразу сохранить объект
        if commit:
            instance.save()

        return instance
