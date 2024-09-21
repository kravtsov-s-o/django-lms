from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
from .models import Question, Category


# Create your views here.
@method_decorator(login_required(login_url='/login/'), name='dispatch')
class FAQView(View):
    def get(self, request):

        categories = Category.objects.all()
        current_category = categories.first().id

        if 'category' in request.GET:
            current_category = int(request.GET['category'])

        questions = Question.objects.filter(category=current_category)

        return render(request, 'faq/index.html',
                      context={
                          'title': 'FAQ',
                          'categories': categories,
                          'current_category': current_category,
                          'questions': questions,
                          'current_page': 'faq'
                      })
