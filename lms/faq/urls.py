from django.urls import path

from faq.views import FAQView

app_name = 'faq'

urlpatterns = [
    path('faq/', FAQView.as_view(), name='faq'),
]
