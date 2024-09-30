import calendar

from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.generic.edit import DeleteView
from datetime import datetime

from .AbstractClasses.BaseAnalyticView import BaseAnalyticView
from .AbstractClasses.ProfileBaseView import ProfileBaseView
from .AbstractClasses.UpdateLessonStatusView import UpdateLessonStatusView
from .models import Student, Teacher, Lesson, StudentProgress
from .forms import LessonForm, LessonMoveForm, ProgressStageForm, UserChangePassword, UserCombineCommonForm
from companies.models import Company
from transactions.models import StudentPayment, TeacherPayment, CompanyPayment
from .services import user_is_student_or_teacher, user_is_teacher, user_is_staff, \
    get_paginator, get_teacher, get_duration_list, generate_month_list_for_filter, get_year_list, \
    sort_data_for_analytics, user_is_lesson_teacher, user_is_student_teacher
from django.utils.translation import gettext_lazy as _


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class MainView(View):
    def get(self, request):
        if request.user.school_role in ['None', 'none', None] and (request.user.is_staff or request.user.is_superuser):
            return redirect(to='admin:index')
        else:
            return redirect(to='school:profile-lessons', pk=request.user.id)


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_teacher, name='dispatch')
class ScheduleView(View):
    def get(self, request, pk):
        current_date = datetime.today()
        current_user = get_teacher(request)

        if request.GET.get('date'):
            current_date = datetime.strptime(request.GET.get('date'), '%Y-%m-%d')

        lessons = Lesson.objects.filter(teacher=current_user, date=current_date).order_by('time')

        # Lessons Filter as Calendar
        year = int(request.GET.get('year', current_date.year))
        month = int(request.GET.get('month', current_date.month))

        month_calendar = calendar.monthcalendar(year, month)

        lessons_list = Lesson.objects.filter(date__year=year, date__month=month)

        lesson_dates = {lesson.date.day for lesson in lessons_list}

        return render(request, 'school/teacher/index.html',
                      context={
                          'title': _('Lesson'),
                          'date': current_date,
                          'lessons': lessons,
                          'lesson_move_form': LessonMoveForm(),
                          'current_user': current_user,
                          'current_page': 'schedule',
                          'year': year,
                          'month': month,
                          'month_list': generate_month_list_for_filter(),
                          'year_list': get_year_list(Lesson, 'date'),
                          'month_calendar': month_calendar,
                          'lesson_dates': lesson_dates,
                      })


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_teacher, name='dispatch')
class LessonAdd(View):
    title = _('Add new lesson')
    def get(self, request, pk):
        teacher = get_teacher(request)

        return render(request,
                      'school/teacher/lesson-add.html',
                      context={
                          'title': self.title,
                          'form': LessonForm(teacher)
                      })

    def post(self, request, pk):
        teacher = get_teacher(request)
        form = LessonForm(teacher, request.POST)

        if form.is_valid():
            form.save()
            return redirect(to='school:cabinet-schedule', pk=request.user.id)
        else:
            return render(request,
                          'school/teacher/lesson-add.html',
                          context={
                              'title': self.title,
                              'form': form
                          })


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_lesson_teacher, name='dispatch')
class LessonEdit(View):
    title = _('Edit lesson')
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        teacher = get_teacher(request)
        lesson = get_object_or_404(Lesson, pk=pk, teacher=teacher)
        form = LessonForm(instance=lesson, teacher=teacher)

        return render(request,
                      'school/teacher/lesson-add.html',
                      context={
                          'title': self.title,
                          'form': form,
                          'lesson': lesson
                      })

    def post(self, request, pk):
        teacher = get_teacher(request)
        lesson = get_object_or_404(Lesson, pk=pk, teacher=teacher)
        form = LessonForm(teacher, request.POST, instance=lesson)

        if form.is_valid():
            form.save()
            return redirect(to='school:cabinet-schedule', pk=request.user.id)
        else:
            return render(request,
                          'school/teacher/lesson-add.html',
                          context={
                              'title': self.title,
                              'form': form
                          })


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_student_or_teacher, name='dispatch')
class LessonView(View):
    def get(self, request, pk):
        lesson = get_object_or_404(Lesson, pk=pk)
        return render(request, 'school/lesson-single.html',
                      context={'lesson': lesson, 'lesson_move_form': LessonMoveForm})


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_lesson_teacher, name='dispatch')
class LessonDelete(View):
    def post(self, request, pk):
        teacher = get_teacher(request)
        lesson = get_object_or_404(Lesson, pk=pk, teacher=teacher)

        if request.method == "POST":
            lesson.delete()
            return redirect(to='school:cabinet-schedule', pk=request.user.id)


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_lesson_teacher, name='dispatch')
class LessonMove(View):
    def post(self, request, pk):
        if request.method == "POST":
            form = LessonMoveForm(request.POST)

            if form.is_valid():
                new_date = form.cleaned_data['date']
                new_time = form.cleaned_data['time']
                teacher = get_teacher(request)
                Lesson.objects.filter(pk=pk, teacher=teacher).update(date=new_date, time=new_time)

                return redirect(to='school:cabinet-schedule', pk=request.user.id)

            return redirect(request.META.get('HTTP_REFERER', '/'))


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_lesson_teacher, name='dispatch')
class LessonConducted(UpdateLessonStatusView):
    def get_status(self):
        return 'conducted'


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_lesson_teacher, name='dispatch')
class LessonMissed(UpdateLessonStatusView):
    def get_status(self):
        return 'missed'


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_lesson_teacher, name='dispatch')
class LessonPlanned(UpdateLessonStatusView):
    def get_status(self):
        return 'planned'


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_teacher, name='dispatch')
class StudentsView(View):
    def get(self, request, pk):
        students = (Student.objects.filter(teacher__user=request.user, user__is_active=True)
                    .order_by('company', 'user__first_name', 'user__last_name'))

        # Start Paginator
        items_per_page = 20
        students_page, page_range = get_paginator(students, items_per_page, request)
        # End Paginator

        return render(request, 'school/teacher/students.html',
                      context={
                          'title': _('Students'),
                          'students': students_page,
                          'page_range': page_range,
                          'current_page': 'students'
                      })


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_teacher, name='dispatch')
class TeacherStatistic(View):
    def get(self, request, pk):
        current_user = get_teacher(request)
        date = datetime.now()
        current_month = date.month
        current_year = date.year
        half_month_summaries = TeacherPayment.objects.get_half_month_summaries(current_user, current_year)

        # =================================================================
        month_salary = ((TeacherPayment
                         .objects
                         .filter(teacher=current_user, created_at__month=current_month, created_at__year=current_year))
                        .aggregate(total_price=Sum('price')))

        teacher_salary = month_salary.get('total_price') if month_salary.get('total_price') is not None else '0.00'

        # =================================================================

        if 'month' in request.GET:
            current_month = int(request.GET['month'])

        if 'year' in request.GET:
            current_year = int(request.GET['year'])

        queryset_lessons = ((TeacherPayment
                             .objects
                             .filter(teacher=current_user, created_at__month=current_month,
                                     created_at__year=current_year))
                            .values('lesson__id', 'lesson__duration__time')
                            .order_by('lesson__id'))

        result = sort_data_for_analytics(queryset_lessons)

        return render(request, 'school/teacher/statistic.html', context={
            'title': _('Statistics'),
            'current_page': 'statistics',
            'sum': half_month_summaries,
            'teacher_salary': teacher_salary,
            'now_date': date,
            'current_user': current_user,
            'current_month': current_month,
            'current_year': current_year,
            'result': result,
            'available_years': get_year_list(TeacherPayment),
            'durations': get_duration_list(),
            'month_list': generate_month_list_for_filter()
        })


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_student_or_teacher, name='dispatch')
class ProfileLessons(ProfileBaseView):
    def get(self, request, pk):
        if self.user.school_role == 'student':
            lessons = Lesson.objects.filter(students=self.current_user).order_by('-date')
        else:
            lessons = Lesson.objects.filter(teacher=self.current_user).order_by('-date')


        items_per_page = 20
        lessons_page, page_range = get_paginator(lessons, items_per_page, request)

        active_page = 'lessons'

        return self.render_page(request, active_page, lessons=lessons_page,
                                page_range=page_range)


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_student_or_teacher, name='dispatch')
class ProfileProgressView(ProfileBaseView):
    active_page = 'progress'
    def get(self, request, pk):
        teacher = get_teacher(request)
        progress_list = StudentProgress.objects.filter(student=self.current_user).order_by('-date')
        return self.render_page(request, self.active_page, progress_list=progress_list, progress_form=ProgressStageForm(self.current_user, teacher))

    def post(self, request, pk):
        teacher = get_teacher(request)
        form = ProgressStageForm(self.current_user, teacher, request.POST)

        if form.is_valid():
            form.save()
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            progress_list = StudentProgress.objects.filter(student=self.current_user)
            return self.render_page(request, self.active_page, progress_list=progress_list, progress_form=form)




@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_student_teacher, name='dispatch')
class ProfileProgressDelete(DeleteView):
    def post(self, request, pk, pk2):
        if request.method == "POST":
            StudentProgress.objects.filter(pk=pk2).delete()
            return redirect(request.META.get('HTTP_REFERER', '/'))


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_student_or_teacher, name='dispatch')
class ProfilePayments(ProfileBaseView):
    def get(self, request, pk):
        if self.user.school_role == 'student':
            payments = StudentPayment.objects.filter(student=self.current_user).order_by('-created_at')
        else:
            payments = TeacherPayment.objects.filter(teacher=self.current_user).order_by('-created_at')

        payments_page, page_range = get_paginator(payments, 20, request)

        active_page = 'payments'

        return self.render_page(request, active_page, payments=payments_page, page_range=page_range)


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_student_or_teacher, name='dispatch')
class ProfileSettings(ProfileBaseView):
    active_page = 'settings'

    def get(self, request, pk):
        teacher = self.current_user if self.user.school_role == 'teacher' else None
        common_form = UserCombineCommonForm(user=self.user, teacher=teacher)
        return self.render_page(request, self.active_page, common_form=common_form, password_form=UserChangePassword)

    def post(self, request, pk):
        teacher = self.current_user if self.user.school_role == 'teacher' else None

        if 'change-password' in request.POST:
            form = UserChangePassword(request.POST, user=self.user)
            if form.is_valid():
                form.save()
                return redirect(request.META.get('HTTP_REFERER', '/'))
            else:
                common_form = UserCombineCommonForm(user=self.user, teacher=teacher)
                return self.render_page(request, self.active_page, common_form=common_form, password_form=form)

        if 'common-information' in request.POST:
            form = UserCombineCommonForm(request.POST, user=self.user, teacher=teacher)
            if form.is_valid():
                form.save(user=self.user, teacher=teacher)
            return redirect(request.META.get('HTTP_REFERER', '/'))


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_staff, name='dispatch')
class AnalyticTeachers(BaseAnalyticView):
    model = TeacherPayment
    current_item_field = 'teacher'
    template_name = 'school/analytics/index.html'
    context_title = _('Teacher Analytics')
    current_page = 'teacher-analytics'

    def get_item_list(self):
        return Teacher.objects.filter(user__is_active=True).order_by('user__first_name', 'user__last_name')

    def get_queryset(self, current_item, current_month, current_year):
        return (self.model.objects
                .filter(teacher=current_item, created_at__month=current_month, created_at__year=current_year)
                .values('lesson__id', 'lesson__duration__time')
                .order_by('lesson__id'))

    def get_month_payment(self, current_item, current_year):
        return self.model.objects.get_half_month_summaries(current_item, current_year)

    def get_context_data(self, request, **kwargs):
        # Вызываем базовый метод, чтобы получить контекст с основными данными
        context = super().get_context_data(request, **kwargs)

        # Используем уже существующие данные из контекста
        current_item = context['current_item']
        current_year = context['current_year']

        # Вызываем get_month_payment и добавляем результат в контекст
        context['month_payment'] = self.get_month_payment(current_item, current_year)
        return context


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_staff, name='dispatch')
class AnalyticCompanies(BaseAnalyticView):
    model = CompanyPayment
    current_item_field = 'company'
    template_name = 'school/analytics/index.html'
    context_title = _('Company Analytics')
    current_page = 'company-analytics'

    def get_item_list(self):
        return Company.objects.filter(is_active=True).order_by('name')

    def get_queryset(self, current_item, current_month, current_year):
        return (self.model.objects
                .filter(company=current_item, created_at__month=current_month, created_at__year=current_year,
                        lesson__isnull=False)
                .values('lesson__id', 'lesson__duration__time')
                .order_by('lesson__id'))

    def get_month_payment(self, current_item, current_year):
        return (self.model.objects
                .filter(company=current_item, created_at__year=current_year)
                .annotate(month=TruncMonth('created_at'))  # Извлекаем месяц из поля created_at
                .values('month')  # Группируем по месяцу
                .annotate(total_price=Sum('price'))  # Суммируем поле price для каждого месяца
                .order_by('month'))

    def get_context_data(self, request, **kwargs):
        # Вызываем базовый метод, чтобы получить контекст с основными данными
        context = super().get_context_data(request, **kwargs)

        # Используем уже существующие данные из контекста
        current_item = context['current_item']
        current_year = context['current_year']

        # Вызываем get_month_payment и добавляем результат в контекст
        context['month_payment'] = self.get_month_payment(current_item, current_year)
        return context
