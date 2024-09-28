from django.urls import path
from .views import MainView, LessonAdd, LessonEdit, LessonView, LessonMove, LessonDelete, LessonConducted, LessonMissed, \
    LessonPlanned, StudentsView, ProfileLessons, ProfileSettings, ProfilePayments, ProfileProgressView, \
    ProfileProgressDelete, ScheduleView, TeacherStatistic, AnalyticTeachers, AnalyticCompanies

app_name = 'school'

urlpatterns = [
    path('', MainView.as_view(), name='main'),

    path('cabinet/<int:pk>/schedule/', ScheduleView.as_view(), name='cabinet-schedule'),
    path('cabinet/<int:pk>/students/', StudentsView.as_view(), name='cabinet-students'),
    path('cabinet/<int:pk>/statistics/', TeacherStatistic.as_view(), name='cabinet-statistics'),
    path('cabinet/<int:pk>/add-lesson/', LessonAdd.as_view(), name='lesson-add'),

    path('lesson/<int:pk>/view/', LessonView.as_view(), name='lesson-view'),
    path('lesson/<int:pk>/edit/', LessonEdit.as_view(), name='lesson-edit'),
    path('lesson/<int:pk>/move/', LessonMove.as_view(), name='lesson-move'),
    path('lesson/<int:pk>/conducted/', LessonConducted.as_view(), name='lesson-conducted'),
    path('lesson/<int:pk>/missed/', LessonMissed.as_view(), name='lesson-missed'),
    path('lesson/<int:pk>/planned/', LessonPlanned.as_view(), name='lesson-planned'),
    path('lesson/<int:pk>/delete/', LessonDelete.as_view(), name='lesson-delete'),

    path('profile/<int:pk>/lessons/', ProfileLessons.as_view(), name='profile-lessons'),
    path('profile/<int:pk>/progress/', ProfileProgressView.as_view(), name='profile-progress'),
    path('profile/<int:pk>/progress/<int:pk2>/delete/', ProfileProgressDelete.as_view(), name='progress-delete'),
    path('profile/<int:pk>/payments/', ProfilePayments.as_view(), name='profile-payments'),
    path('profile/<int:pk>/settings/', ProfileSettings.as_view(), name='profile-settings'),

    path('analytics/teachers/', AnalyticTeachers.as_view(), name='analytic-teachers'),
    path('analytics/companies/', AnalyticCompanies.as_view(), name='analytic-companies'),
]


