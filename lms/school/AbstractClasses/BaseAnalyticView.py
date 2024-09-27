from abc import ABC, abstractmethod
from datetime import datetime

from django.shortcuts import render
from django.views import View

from school.services import get_year_list, get_duration_list, generate_month_list_for_filter, \
    sort_data_for_analytics


class BaseAnalyticView(ABC, View):
    model = None
    current_item_field = None
    template_name = None
    context_title = None
    current_page = None

    def get_current_month_and_year(self, request):
        date = datetime.now()
        current_month = date.month
        current_year = date.year

        if 'month' in request.GET:
            current_month = int(request.GET['month'])

        if 'year' in request.GET:
            current_year = int(request.GET['year'])

        return current_month, current_year

    def get_current_item(self, request, item_list, current_item_field):
        current_item = item_list.first()

        if current_item_field in request.GET:
            current_item = int(request.GET[current_item_field])

        return current_item

    def get_context_data(self, request, **kwargs):
        item_list = self.get_item_list()
        current_item = self.get_current_item(request, item_list, self.current_item_field)
        current_month, current_year = self.get_current_month_and_year(request)

        if 'item' in request.GET:
            current_item = int(request.GET['item'])

        queryset = self.get_queryset(current_item, current_month, current_year)
        result = sort_data_for_analytics(queryset)

        context = {
            'title': self.context_title,
            'current_page': self.current_page,
            'current_month': current_month,
            'current_year': current_year,
            'current_item': current_item,
            'item_list': item_list,
            'result': result,
            'available_years': get_year_list(self.model),
            'durations': get_duration_list(),
            'month_list': generate_month_list_for_filter()
        }
        context.update(kwargs)
        return context

    def render_page(self, request, **kwargs):
        """
        Вспомогательный метод для рендеринга страницы с заданным контекстом.
        """
        context = self.get_context_data(request, **kwargs)
        return render(request, self.template_name, context)

    def get(self, request):
        return self.render_page(request)

    @abstractmethod
    def get_item_list(self):
        raise NotImplementedError("You must implement get_item_list() in subclasses.")

    @abstractmethod
    def get_queryset(self, current_item, current_month, current_year):
        raise NotImplementedError("You must implement get_queryset() in subclasses.")
