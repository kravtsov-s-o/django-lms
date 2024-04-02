from django.urls import path
from .views import MainView, LessonAdd, LessonSingle, StudentsView

app_name = 'school'

urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('lesson/add/', LessonAdd.as_view(), name='lesson-add'),
    path('students/', StudentsView.as_view(), name='students'),
    path('lesson/view/<int:pk>/', LessonSingle.as_view(), name='lesson-view'),
]
