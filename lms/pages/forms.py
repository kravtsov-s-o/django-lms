from django import forms
from django.utils.text import slugify
from django_ckeditor_5.widgets import CKEditor5Widget

from .models import Page


class PageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = '__all__'
        widgets = {
            'content': CKEditor5Widget(config_name='default', attrs={'style': 'width: 80%;'})
        }

    def save(self, commit=True):
        instance = super(PageForm, self).save(commit=False)

        if not instance.slug:
            instance.slug = slugify(instance.title)

        if commit:
            instance.save()

        return instance
