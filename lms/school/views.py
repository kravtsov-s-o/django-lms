from abc import ABC, abstractmethod
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.edit import DeleteView
from datetime import datetime
from .models import Student, Teacher, Lesson, StudentProgress
from .forms import LessonForm, LessonMoveForm, ProgressStageForm
from .services import lesson_finished, user_is_student_or_teacher_or_staff
from users.models import User


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
class ScheduleView(View):
    def get(self, request):
        current_date = datetime.today()

        if request.GET.get('date'):
            current_date = datetime.strptime(request.GET.get('date'), '%Y-%m-%d')

        lessons = Lesson.objects.filter(teacher__user=request.user, date=current_date).order_by('time')

        return render(request, 'school/teacher/index.html',
                      context={
                          'title': 'Lesson',
                          'date': current_date,
                          'lessons': lessons,
                          'lesson_move_form': LessonMoveForm(),
                          'current_page': 'schedule'
                      })


@method_decorator(login_required(login_url='/login/'), name='dispatch')
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
            return redirect(to='school:cabinet-schedule')
        else:
            return render(request,
                          'school/teacher/lesson-add.html',
                          context={
                              'title': 'Add new lesson',
                              'form': form
                          })


@method_decorator(login_required(login_url='/login/'), name='dispatch')
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
            return redirect(to='school:cabinet-schedule')
        else:
            return render(request,
                          'school/teacher/lesson-add.html',
                          context={
                              'title': 'Edit lesson',
                              'form': form
                          })


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class LessonView(View):
    def get(self, request, pk):
        teacher = Teacher.objects.filter(user=request.user).first()
        lesson = get_object_or_404(Lesson, pk=pk, teacher=teacher)
        return render(request, 'school/lesson-single.html',
                      context={'lesson': lesson, 'lesson_move_form': LessonMoveForm})


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class LessonDelete(View):
    def post(self, request, pk):
        teacher = Teacher.objects.filter(user=request.user).first()
        lesson = get_object_or_404(Lesson, pk=pk, teacher=teacher)

        if request.method == "POST":
            lesson.delete()
            return redirect(request.META.get('HTTP_REFERER', '/'))


@method_decorator(login_required(login_url='/login/'), name='dispatch')
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


class LessonConducted(UpdateLessonStatusView):
    def get_status(self):
        return 'сonducted'


class LessonMissed(UpdateLessonStatusView):
    def get_status(self):
        return 'missed'


class LessonPlanned(UpdateLessonStatusView):
    def get_status(self):
        return 'planned'


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class StudentsView(View):
    def get(self, request):
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
@method_decorator(user_is_student_or_teacher_or_staff, name='dispatch')
class ProfileLessons(View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.school_role == 'student':
            current_user = get_object_or_404(Student, user=user.id)
            lessons = Lesson.objects.filter(students=current_user).order_by('-date')
        else:
            current_user = get_object_or_404(Teacher, user=user.id)
            lessons = Lesson.objects.filter(teacher=current_user).order_by('-date')

        current_user_rate = int(current_user.rate)

        items_per_page = 20
        lessons_page, page_range = get_paginator(lessons, items_per_page, request)

        return render(request, 'school/profile/index.html',
                      context={
                          'title': 'Profile',
                          'tab': 'lessons',
                          'current_user_rate': current_user_rate,
                          'current_user': current_user,
                          'lessons': lessons_page,
                          'page_range': page_range
                      })


@method_decorator(login_required(login_url='/login/'), name='dispatch')
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

        return render(request, 'school/profile/index.html',
                      context={
                          'title': 'Profile',
                          'tab': 'progress',
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
class ProfileProgressDelete(DeleteView):
    def post(self, request, pk, pk2):
        if request.method == "POST":
            StudentProgress.objects.filter(pk=pk2).delete()
            return redirect(request.META.get('HTTP_REFERER', '/'))
