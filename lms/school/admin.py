from django.contrib import admin
from .models import Teacher, Student, Lesson, StudentProgress
from .forms import TeacherForm, StudentForm
from users.models import User
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import gettext_lazy as _

from .services import lesson_finished


# Register your models here.
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email']
    list_display = ['get_name', 'get_languages', 'rate', 'currency']
    list_filter = ['language', 'user__is_active']

    form = TeacherForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'user':
            # Filter users by school_role='teacher'
            field.queryset = User.objects.filter(school_role='teacher')
        return field

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

    form = StudentForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'user':
            # Filter users by по school_role='student'
            field.queryset = User.objects.filter(school_role='student')
        return field

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
def make_conducted(modeladmin, request, queryset):
    for lesson in queryset:
        lesson_finished(lesson.teacher, lesson.id, 'conducted')


@admin.action(description=_("Mark lesson as 'Missed'"))
def make_missed(modeladmin, request, queryset):
    for lesson in queryset:
        lesson_finished(lesson.teacher, lesson.id, 'missed')


@admin.action(description=_("Mark lesson as 'Planned'"))
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
