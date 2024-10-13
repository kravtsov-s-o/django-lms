from decimal import Decimal

from django.shortcuts import get_object_or_404, render
from django.views import View

from users.models import User

from school.models import Student, Teacher
from school.services import count_time_left

from django.utils.translation import gettext_lazy as _


class ProfileBaseView(View):
    """
    Базовый класс для всех вкладок профиля.
    """

    def dispatch(self, request, *args, **kwargs):
        self.user = get_object_or_404(User, pk=kwargs.get('pk'))
        self.current_user = self.get_current_user(self.user)
        self.current_user_rate = int(self.current_user.price_plan.price)\
            if self.current_user.price_plan.discount == 0\
            else round(self.current_user.price_plan.price - (self.current_user.price_plan.price * Decimal(self.current_user.price_plan.discount / 100)))
        self.current_user_rate_old = int(self.current_user.price_plan.price)
        return super().dispatch(request, *args, **kwargs)

    def get_current_user(self, user):
        """
        Определение текущего пользователя в зависимости от его роли.
        """
        if user.school_role == User.SchoolRole.STUDENT:
            return get_object_or_404(Student, user=user.id)
        return get_object_or_404(Teacher, user=user.id)


    def get_Lesson_time_left(self):
        lessons_left = 0

        if self.user.school_role == User.SchoolRole.STUDENT:
            lessons_left = count_time_left(self.current_user)

        return lessons_left

    def get_context_data(self, **kwargs):
        """
        Общий контекст для всех вкладок профиля.
        """
        context = {
            'title': _('Profile'),
            'current_user': self.current_user,
            'current_user_rate': self.current_user_rate,
            'current_user_rate_old': self.current_user_rate_old,
            'lessons_left': self.get_Lesson_time_left(),
        }
        context.update(kwargs)
        return context

    def render_page(self, request, active_page, template='school/profile/index.html', **kwargs):
        """
        Вспомогательная функция рендеринга страницы.
        """
        context = self.get_context_data(tab=active_page, current_page=active_page, **kwargs)
        return render(request, template, context)
