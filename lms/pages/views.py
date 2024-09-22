from django.shortcuts import render, get_object_or_404
from django.views import View

from .models import Page


# Create your views here.
class PageView(View):
    def get(self, request, slug):
        page = get_object_or_404(Page, slug=slug)
        return render(self.request, 'pages/text-page.html',
                      context={
                          'page': page
                      })
