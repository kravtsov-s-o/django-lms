from abc import ABC, abstractmethod

from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect
from django.views import View

from school.services import get_teacher, lesson_finished
from django.utils.translation import gettext_lazy as _


class UpdateLessonStatusView(ABC, View):
    @abstractmethod
    def get_status(self):
        pass

    @transaction.atomic
    def update_lesson_status(self, request, pk):
        teacher = get_teacher(request)

        lesson_finished(teacher, pk, self.get_status())

    def post(self, request, pk):
        self.update_lesson_status(request, pk)

        messages.success(request, _('Lesson status was changed. {status}').format(status=self.get_status()))
        return redirect(request.META.get('HTTP_REFERER', '/'))
