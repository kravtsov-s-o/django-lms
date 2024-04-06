from django.urls import path
from .views import MainView, LessonAdd, LessonEdit, LessonView, LessonMove, LessonDelete, LessonConducted, LessonMissed, \
    LessonPlanned, StudentsView

app_name = 'school'

urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('students/', StudentsView.as_view(), name='students'),
    path('lesson/add/', LessonAdd.as_view(), name='lesson-add'),
    path('lesson/<int:pk>/view/', LessonView.as_view(), name='lesson-view'),
    path('lesson/<int:pk>/edit/', LessonEdit.as_view(), name='lesson-edit'),
    path('lesson/<int:pk>/move/', LessonMove.as_view(), name='lesson-move'),
    path('lesson/<int:pk>/conducted/', LessonConducted.as_view(), name='lesson-conducted'),
    path('lesson/<int:pk>/missed/', LessonMissed.as_view(), name='lesson-missed'),
    path('lesson/<int:pk>/planned/', LessonPlanned.as_view(), name='lesson-planned'),
    path('lesson/<int:pk>/delete/', LessonDelete.as_view(), name='lesson-delete'),
]
