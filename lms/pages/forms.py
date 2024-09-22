from django import forms
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field

from .models import Page


class PageForm(forms.ModelForm):
    content = CKEditor5Field('Text', config_name='extends')

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
