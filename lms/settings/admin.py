from django.contrib import admin
from .models import Language, Duration, Currency


# Register your models here.
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'symbol', 'exchange', 'default']
    readonly_fields = ['default']

    def has_delete_permission(self, request, obj=None):
        # Запретить удаление, если объект является стандартным
        if obj and obj.default:
            return False
        return super().has_delete_permission(request, obj)


admin.site.register(Language)
admin.site.register(Duration)
admin.site.register(Currency, CurrencyAdmin)
