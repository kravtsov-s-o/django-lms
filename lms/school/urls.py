from django.urls import path
from .views import MainView, LessonAdd, LessonEdit, LessonSingle, StudentsView

app_name = 'school'

urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('students/', StudentsView.as_view(), name='students'),
    path('lesson/add/', LessonAdd.as_view(), name='lesson-add'),
    path('lesson/<int:pk>/view/', LessonSingle.as_view(), name='lesson-view'),
    path('lesson/<int:pk>/edit/', LessonEdit.as_view(), name='lesson-edit'),
]
