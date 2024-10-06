from django.contrib import admin
from django.db import transaction

from .models import Teacher, Student, Lesson, StudentProgress
from .forms import TeacherForm, StudentForm
from django.utils.translation import gettext_lazy as _

from .services import lesson_finished


# Register your models here.
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email']
    list_display = ['get_name', 'get_languages', 'rate', 'currency']
    list_filter = ['language', 'user__is_active']

    add_fieldsets = (
        (_('Base info'), {
            'fields': ('username', 'password1', 'password2',)
        }),
        (_('User info'), {
            'fields': ('first_name', 'last_name', 'email',)
        }),
        (_('School info'), {
            'fields': ('school_role', 'language', 'rate', 'currency', 'about'),
        }),
    )

    edit_fieldsets = (
        (_('Base info'), {
            'fields': ('username', 'password',)
        }),
        (_('User info'), {
            'fields': ('first_name', 'last_name', 'email',)
        }),
        (_('School info'), {
            'fields': ('school_role', 'language', 'rate', 'currency', 'about'),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        """
        Generate fieldset for add or edit user.
        """
        if obj:
            return self.edit_fieldsets
        else:
            return self.add_fieldsets

    form = TeacherForm

    def get_name(self, obj):
        if obj.user.first_name == '' and obj.user.last_name == '':
            return f'{obj.user.username}'

        return f'{obj.user.first_name} {obj.user.last_name}'

    def get_languages(self, obj):
        return ', '.join([language.name for language in obj.language.all()])

    get_name.short_description = _('Name')
    get_languages.short_description = _('Languages')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email']
    list_display = ['get_name', 'teacher', 'get_languages', 'rate', 'wallet', 'currency', 'company']
    list_filter = ['language', 'company', 'teacher', 'user__is_active']

    add_fieldsets = (
        ('Base info', {
            'fields': ('username', 'password1', 'password2',)
        }),
        ('User info', {
            'fields': ('first_name', 'last_name', 'email',)
        }),
        ('School info', {
            'fields': ('school_role', 'language', 'teacher', 'rate', 'wallet', 'currency', 'company'),
        }),
    )

    edit_fieldsets = (
        ('Base info', {
            'fields': ('username', 'password',)
        }),
        ('User info', {
            'fields': ('first_name', 'last_name', 'email',)
        }),
        ('School info', {
            'fields': ('school_role', 'language', 'teacher', 'rate', 'wallet', 'currency', 'company'),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        """
        Generate fieldset for add or edit user.
        """
        if obj:
            return self.edit_fieldsets
        else:
            return self.add_fieldsets

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

    get_name.short_description = _('Name')
    get_languages.short_description = _('Languages')
    get_balance.short_description = _('Wallet')


@admin.action(description=_("Mark lesson as 'Conducted'"))
@transaction.atomic
def make_conducted(modeladmin, request, queryset):
    for lesson in queryset:
        lesson_finished(lesson.teacher, lesson.id, 'conducted')


@admin.action(description=_("Mark lesson as 'Missed'"))
@transaction.atomic
def make_missed(modeladmin, request, queryset):
    for lesson in queryset:
        lesson_finished(lesson.teacher, lesson.id, 'missed')


@admin.action(description=_("Mark lesson as 'Planned'"))
@transaction.atomic
def make_planned(modeladmin, request, queryset):
    for lesson in queryset:
        lesson_finished(lesson.teacher, lesson.id, 'planned')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    search_fields = ['students__user__username', 'students__user__first_name', 'students__user__last_name',
                     'students__user__email']
    list_display = ['theme', 'date', 'time', 'status', 'get_students', 'teacher', 'price', 'currency']
    list_filter = ['status', 'students', 'teacher']
    readonly_fields = ['status', 'price', 'currency']

    def get_students(self, obj):
        return ", ".join([str(student) for student in obj.students.all()])

    actions = [make_conducted, make_missed, make_planned]


@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'student', 'date']
    list_filter = ['teacher', 'student']
