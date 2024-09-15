import json
from abc import ABC, abstractmethod
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.edit import DeleteView
from datetime import datetime
from .models import Student, Teacher, Lesson, StudentProgress
from .forms import LessonForm, LessonMoveForm, ProgressStageForm, UserChangePassword, UserCombineCommonForm
from .services import lesson_finished, user_is_student_or_teacher, count_time_left, user_is_teacher
from users.models import User

from transactions.models import StudentPayment, TeacherPayment


# Create your views here.
def get_paginator(items, items_per_page, request):
    paginator = Paginator(items, items_per_page)

    page = request.GET.get("page")

    try:
        items_page = paginator.page(page)
    except PageNotAnInteger:
        items_page = paginator.page(1)
    except EmptyPage:
        items_page = paginator.page(paginator.num_pages)

    page_range = range(1, items_page.paginator.num_pages + 1)

    return items_page, page_range


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class MainView(View):
    def get(self, request):
        return redirect(to='school:profile-lessons', pk=request.user.id)


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_teacher, name='dispatch')
class ScheduleView(View):
    def get(self, request, pk):
        current_date = datetime.today()

        user = get_object_or_404(User, pk=pk)
        current_user = get_object_or_404(Teacher, user=user.id)

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
@method_decorator(user_is_teacher, name='dispatch')
class LessonAdd(View):
    def get_teacher(self, request):
        return Teacher.objects.filter(user=request.user).first()

    def get(self, request):
        teacher = self.get_teacher(request)

        return render(request,
                      'school/teacher/lesson-add.html',
                      context={
                          'title': 'Add new lesson',
                          'form': LessonForm(teacher)
                      })

    def post(self, request):
        teacher = self.get_teacher(request)
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
@method_decorator(user_is_teacher, name='dispatch')
class LessonEdit(View):
    def get_teacher(self, request):
        return Teacher.objects.filter(user=request.user).first()

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        teacher = self.get_teacher(request)
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
        teacher = self.get_teacher(request)
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
@method_decorator(user_is_teacher, name='dispatch')
class LessonDelete(View):
    def post(self, request, pk):
        teacher = Teacher.objects.filter(user=request.user).first()
        lesson = get_object_or_404(Lesson, pk=pk, teacher=teacher)

        if request.method == "POST":
            lesson.delete()
            return redirect(to='school:cabinet-schedule', pk=request.user.id)


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_teacher, name='dispatch')
class LessonMove(View):
    def post(self, request, pk):
        if request.method == "POST":
            form = LessonMoveForm(request.POST)

            if form.is_valid():
                new_date = form.cleaned_data['date']
                new_time = form.cleaned_data['time']
                teacher = Teacher.objects.filter(user=request.user).first()
                Lesson.objects.filter(pk=pk, teacher=teacher).update(date=new_date, time=new_time)
                return redirect(to='school:cabinet-schedule')
            return redirect(request.META.get('HTTP_REFERER', '/'))


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_teacher, name='dispatch')
class UpdateLessonStatusView(ABC, View):
    @abstractmethod
    def get_status(self):
        pass

    @transaction.atomic
    def update_lesson_status(self, request, pk):
        teacher = Teacher.objects.filter(user=request.user).first()

        lesson_finished(teacher, pk, self.get_status())

    def post(self, request, pk):
        self.update_lesson_status(request, pk)
        return redirect(request.META.get('HTTP_REFERER', '/'))


@method_decorator(user_is_teacher, name='dispatch')
class LessonConducted(UpdateLessonStatusView):
    def get_status(self):
        return 'сonducted'


@method_decorator(user_is_teacher, name='dispatch')
class LessonMissed(UpdateLessonStatusView):
    def get_status(self):
        return 'missed'


@method_decorator(user_is_teacher, name='dispatch')
class LessonPlanned(UpdateLessonStatusView):
    def get_status(self):
        return 'planned'


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_teacher, name='dispatch')
class StudentsView(View):
    def get(self, request, pk):
        students = (Student.objects.filter(teacher__user=request.user, user__is_active=True)
                    .order_by('user__first_name', 'user__last_name'))

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
        date = datetime.now()
        current_month = date.month
        current_year = date.year
        half_month_summaries = TeacherPayment.objects.get_half_month_summaries(request.user, current_year)

        # =================================================================
        teacher_salary = ((TeacherPayment
                          .objects
                          .filter(teacher__user=request.user, created_at__month=current_month, created_at__year=current_year))
                          .aggregate(total_price=Sum('price')))

        lessons = (
            Lesson.objects
            .filter(teacher__user=request.user, date__year=current_year)
            .annotate(month=TruncMonth('date'))
            .values('month', 'currency__name')
            .annotate(total_price=Sum('price'))
            .order_by('month', 'currency__name')
        )

        data = {}
        for lesson in lessons:
            month = lesson['month'].strftime('%Y-%m')
            currency = lesson['currency__name']
            total_price = float(lesson['total_price'])
            if month not in data:
                data[month] = {}
            data[month][currency] = total_price

        chart_data = {
            'months': sorted(data.keys()),
            'currencies': list({currency for month in data.values() for currency in month.keys()}),
            'series': {currency: [data[month].get(currency, 0) for month in sorted(data.keys())] for currency in
                       {currency for month in data.values() for currency in month.keys()}}
        }

        # =================================================================

        return render(request, 'school/teacher/statistic.html', context={
            'current_page': 'statistics',
            'sum': half_month_summaries,
            'chart_data': json.dumps(chart_data),
            'teacher_salary': teacher_salary,
            'now_date': date,
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
    def _get_teacher(self, request):
        return Teacher.objects.filter(user=request.user).first()

    def _get_student(self, pk):
        return get_object_or_404(Student, pk=pk)

    def get(self, request, pk):
        student = self._get_student(pk)
        teacher = self._get_teacher(request)
        student_rate = int(student.rate)

        progress_list = StudentProgress.objects.filter(student=student).order_by('-date')

        items_per_page = 20

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
        teacher = self._get_teacher(request)
        form = ProgressStageForm(student, teacher, request.POST)

        print(form.is_valid())

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
                    return self._render_page(request, active_page, current_user_rate, current_user, form, UserChangePassword)

        return redirect(request.META.get('HTTP_REFERER', '/'))
