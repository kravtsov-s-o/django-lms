from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.generic.edit import DeleteView
from datetime import datetime

from .AbstractClasses.BaseAnalyticView import BaseAnalyticView
from .AbstractClasses.UpdateLessonStatusView import UpdateLessonStatusView
from .models import Student, Teacher, Lesson, StudentProgress
from .forms import LessonForm, LessonMoveForm, ProgressStageForm, UserChangePassword, UserCombineCommonForm
from companies.models import Company
from users.models import User
from transactions.models import StudentPayment, TeacherPayment, CompanyPayment
from .services import user_is_student_or_teacher, count_time_left, user_is_teacher, user_is_staff, \
    get_paginator, get_teacher, get_duration_list, generate_month_list_for_filter, get_payment_year_list, \
    sort_data_for_analytics, user_is_lesson_teacher


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

        return render(request, 'school/teacher/index.html',
                      context={
                          'title': 'Lesson',
                          'date': current_date,
                          'lessons': lessons,
                          'lesson_move_form': LessonMoveForm(),
                          'current_user': current_user,
                          'current_page': 'schedule'
                      })


@method_decorator(login_required(login_url='/login/'), name='dispatch')
# @method_decorator(user_is_teacher, name='dispatch')
class LessonAdd(View):
    def get(self, request):
        teacher = get_teacher(request)

        return render(request,
                      'school/teacher/lesson-add.html',
                      context={
                          'title': 'Add new lesson',
                          'form': LessonForm(teacher)
                      })

    def post(self, request):
        teacher = get_teacher(request)
        form = LessonForm(teacher, request.POST)

        if form.is_valid():
            form.save()
            return redirect(to='school:cabinet-schedule', pk=request.user.id)
        else:
            return render(request,
                          'school/teacher/lesson-add.html',
                          context={
                              'title': 'Add new lesson',
                              'form': form
                          })


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_lesson_teacher, name='dispatch')
class LessonEdit(View):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        teacher = get_teacher(request)
        lesson = get_object_or_404(Lesson, pk=pk, teacher=teacher)
        form = LessonForm(instance=lesson, teacher=teacher)

        return render(request,
                      'school/teacher/lesson-add.html',
                      context={
                          'title': 'Edit lesson',
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
                              'title': 'Edit lesson',
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
                          'title': 'Students',
                          'students': students_page,
                          'page_range': page_range,
                          'current_page': 'students'}
                      )


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_teacher, name='dispatch')
class TeacherStatistic(View):
    def get(self, request, pk):
        current_user = get_teacher(request)
        date = datetime.now()
        current_month = date.month
        current_year = date.year
        half_month_summaries = TeacherPayment.objects.get_half_month_summaries(request.user, current_year)

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
            'title': 'Statistics',
            'current_page': 'statistics',
            'sum': half_month_summaries,
            'teacher_salary': teacher_salary,
            'now_date': date,
            'current_user': current_user,
            'current_month': current_month,
            'current_year': current_year,
            'result': result,
            'available_years': get_payment_year_list(TeacherPayment),
            'durations': get_duration_list(),
            'month_list': generate_month_list_for_filter()
        })


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_student_or_teacher, name='dispatch')
class ProfileLessons(View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.school_role == 'student':
            current_user = get_object_or_404(Student, user=user.id)
            lessons = Lesson.objects.filter(students=current_user).order_by('-date')
            lessons_left = count_time_left(current_user)
        else:
            current_user = get_object_or_404(Teacher, user=user.id)
            lessons = Lesson.objects.filter(teacher=current_user).order_by('-date')
            lessons_left = 0

        current_user_rate = int(current_user.rate)

        items_per_page = 20
        lessons_page, page_range = get_paginator(lessons, items_per_page, request)

        active_page = 'lessons'

        return render(request, 'school/profile/index.html',
                      context={
                          'title': 'Profile',
                          'tab': active_page,
                          'current_page': active_page,
                          'current_user_rate': current_user_rate,
                          'current_user': current_user,
                          'lessons_left': lessons_left,
                          'lessons': lessons_page,
                          'page_range': page_range
                      })


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_student_or_teacher, name='dispatch')
class ProfileProgressView(View):
    def _get_student(self, pk):
        return get_object_or_404(Student, pk=pk)

    def get(self, request, pk):
        student = self._get_student(pk)
        teacher = get_teacher(request)
        student_rate = int(student.rate)

        progress_list = StudentProgress.objects.filter(student=student).order_by('-date')

        active_page = 'progress'

        return render(request, 'school/profile/index.html',
                      context={
                          'title': 'Profile',
                          'tab': active_page,
                          'current_page': active_page,
                          'student_rate': student_rate,
                          'current_user': student,
                          'progress_list': progress_list,
                          'progress_form': ProgressStageForm(student, teacher)
                      })

    def post(self, request, pk):
        student = self._get_student(pk)
        teacher = get_teacher(request)
        form = ProgressStageForm(student, teacher, request.POST)

        if form.is_valid():
            form.save()
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            student_rate = int(student.rate)
            progress_list = StudentProgress.objects.filter(student=student)
            return render(request, 'school/profile/index.html',
                          context={
                              'title': 'Profile',
                              'tab': 'progress',
                              'student_rate': student_rate,
                              'current_user': student,
                              'progress_list': progress_list,
                              'progress_form': form
                          })


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_teacher, name='dispatch')
class ProfileProgressDelete(DeleteView):
    def post(self, request, pk, pk2):
        if request.method == "POST":
            StudentProgress.objects.filter(pk=pk2).delete()
            return redirect(request.META.get('HTTP_REFERER', '/'))


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_student_or_teacher, name='dispatch')
class ProfilePayments(View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.school_role == 'student':
            current_user = get_object_or_404(Student, user=user.id)
            payments = StudentPayment.objects.filter(student=current_user).order_by('-created_at')
        else:
            current_user = get_object_or_404(Teacher, user=user.id)
            payments = TeacherPayment.objects.filter(teacher=current_user).order_by('-created_at')

        current_user_rate = int(current_user.rate)

        items_per_page = 20
        payments_page, page_range = get_paginator(payments, items_per_page, request)

        active_page = 'payments'

        return render(request, 'school/profile/index.html',
                      context={
                          'title': 'Profile',
                          'tab': active_page,
                          'current_page': active_page,
                          'current_user_rate': current_user_rate,
                          'current_user': current_user,
                          'payments': payments_page,
                          'page_range': page_range
                      })


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_student_or_teacher, name='dispatch')
class ProfileSettings(View):
    def _get_user(self, pk):
        return get_object_or_404(User, pk=pk)

    def _get_sub_info(self, user):
        if user.school_role == 'student':
            current_user = get_object_or_404(Student, user=user.id)
        else:
            current_user = get_object_or_404(Teacher, user=user.id)

        return current_user

    def _render_page(self, request, active_page, current_user_rate, current_user, common_form, password_form):
        return render(request, 'school/profile/index.html',
                      context={
                          'title': 'Profile',
                          'tab': active_page,
                          'current_page': active_page,
                          'current_user_rate': current_user_rate,
                          'current_user': current_user,
                          'common_form': common_form,
                          'password_form': password_form
                      })

    def get(self, request, pk):
        active_page = 'settings'
        user = self._get_user(pk)
        current_user = self._get_sub_info(user)
        teacher = current_user if user.school_role == 'teacher' else None
        current_user_rate = int(current_user.rate)

        common_form = UserCombineCommonForm(user=user, teacher=teacher)

        return self._render_page(request, active_page, current_user_rate, current_user, common_form, UserChangePassword)

    def post(self, request, pk, *args, **kwargs):
        if request.method == "POST":
            user = self._get_user(pk)
            current_user = self._get_sub_info(user)
            teacher = current_user if user.school_role == 'teacher' else None
            current_user_rate = int(current_user.rate)
            active_page = 'settings'

            if 'change-password' in request.POST:
                form = UserChangePassword(request.POST, user=user)

                if form.is_valid():
                    form.save()
                else:
                    common_form = UserCombineCommonForm(user=user, teacher=teacher)

                    return self._render_page(request, active_page, current_user_rate, current_user, common_form, form)

            if 'common-information' in request.POST:
                form = UserCombineCommonForm(request.POST, user=user, teacher=teacher)

                if form.is_valid():
                    form.save(user=user, teacher=teacher)
                else:
                    return self._render_page(request, active_page, current_user_rate, current_user, form,
                                             UserChangePassword)

        return redirect(request.META.get('HTTP_REFERER', '/'))


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_staff, name='dispatch')
class AnalyticTeachers(BaseAnalyticView):
    model = TeacherPayment
    current_item_field = 'teacher'
    template_name = 'school/analytics/index.html'
    context_title = 'Teacher Analytics'
    current_page = 'teacher-analytics'

    def get_item_list(self):
        return Teacher.objects.filter(user__is_active=True).order_by('user__first_name', 'user__last_name')

    def get_queryset(self, current_item, current_month, current_year):
        return (TeacherPayment.objects
                .filter(teacher=current_item, created_at__month=current_month, created_at__year=current_year)
                .values('lesson__id', 'lesson__duration__time')
                .order_by('lesson__id'))


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_staff, name='dispatch')
class AnalyticCompanies(BaseAnalyticView):
    model = CompanyPayment
    current_item_field = 'company'
    template_name = 'school/analytics/index.html'
    context_title = 'Company Analytics'
    current_page = 'company-analytics'

    def get_item_list(self):
        return Company.objects.filter(is_active=True).order_by('name')

    def get_queryset(self, current_item, current_month, current_year):
        return (CompanyPayment.objects
                .filter(company=current_item, created_at__month=current_month, created_at__year=current_year, lesson__isnull=False)
                .values('lesson__id', 'lesson__duration__time')
                .order_by('lesson__id'))

