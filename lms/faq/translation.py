from modeltranslation.translator import register, TranslationOptions
from .models import Category, Question


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(Question)
class QuestionTranslationOptions(TranslationOptions):
    fields = ('question', 'answer')
