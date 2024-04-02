from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
from datetime import datetime
from users.models import User
from .models import Student, Teacher, Lesson
from .forms import LessonForm


# Create your views here.
@method_decorator(login_required(login_url='/login/'), name='dispatch')
class MainView(View):
    def get(self, request):

        current_date = datetime.today()

        if request.GET.get('date'):
            current_date = datetime.strptime(request.GET.get('date'), '%Y-%m-%d')

        lessons = Lesson.objects.filter(teacher=GetTeacher.get(user=request.user), date=current_date).order_by('time')

        return render(request, 'school/teacher/index.html',
                      context={
                          'title': 'Lesson',
                          'date': current_date,
                          'lessons': lessons
                      })


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class LessonAdd(View):
    def get(self, request):
        teacher = GetTeacher.get(request.user)

        return render(request, 'school/teacher/lesson-add.html', context={'title': 'Add new lesson', 'form': LessonForm(teacher)})


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class LessonSingle(View):
    def get(self, request, pk):
        return render(request, 'school/lesson-single.html')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class StudentsView(View):
    def get(self, request):
        students = Student.objects.filter(teacher=GetTeacher.get(user=request.user))

        return render(request, 'school/teacher/students.html',
                      context={'students': students}
                      )


class GetTeacher:
    @staticmethod
    def get(user: User) -> Teacher:
        return Teacher.objects.filter(user=user).first()
