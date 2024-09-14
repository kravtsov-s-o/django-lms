from django.contrib import admin
from .models import Teacher, Student, Lesson
from .forms import TeacherForm, StudentForm
from users.models import User
from django.contrib.auth.forms import UserChangeForm


# Register your models here.
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email']
    list_display = ['get_name', 'get_languages', 'rate', 'currency']
    list_filter = ['language', 'user__is_active']

    form = TeacherForm

    def get_name(self, obj):
        if obj.user.first_name == '' and obj.user.last_name == '':
            return f'{obj.user.username}'

        return f'{obj.user.first_name} {obj.user.last_name}'

    def get_languages(self, obj):
        return ', '.join([language.name for language in obj.language.all()])

    get_name.short_description = 'Name'
    get_languages.short_description = 'Languages'


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email']
    list_display = ['get_name', 'teacher', 'get_languages', 'rate', 'wallet', 'currency', 'company']
    list_filter = ['language', 'company', 'teacher', 'user__is_active']

    form = StudentForm

    def get_name(self, obj):
        if obj.user.first_name == '' and obj.user.last_name == '':
            return f'{obj.user.username}'

        return f'{obj.user.first_name} {obj.user.last_name}'

    def get_balance(self, obj):
        return f'{obj.wallet} {obj.currency}'

    def get_languages(self, obj):
        return ', '.join([language.name for language in obj.language.all()])

    def get_company(self, obj):
        return f'{obj.company.name}'

    get_name.short_description = 'Name'
    get_languages.short_description = 'Languages'
    get_balance.short_description = 'Wallet'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    # search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email']
    list_display = ['theme', 'date', 'time', 'status', 'teacher', 'price', 'currency']
    # list_filter = ['language', 'company', 'teacher', 'user__is_active']

