from django.contrib import admin
from .models import Language, Duration, Currency


# Register your models here.
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'exchange', 'default']


admin.site.register(Language)
admin.site.register(Duration)
admin.site.register(Currency, CurrencyAdmin)
