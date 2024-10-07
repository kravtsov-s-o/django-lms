from modeltranslation.translator import register, TranslationOptions
from .models import TransactionType


@register(TransactionType)
class TransactionTypeTranslationOptions(TranslationOptions):
    fields = ('title','description',)

