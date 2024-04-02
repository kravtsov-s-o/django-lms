from django.contrib import admin
from .models import Company

# Register your models here.
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'wallet', 'currency', 'rate', 'discount')

admin.site.register(Company, CompanyAdmin)