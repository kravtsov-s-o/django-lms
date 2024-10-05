from django.urls import path
from .views import PaymentView

app_name = 'transactions'

urlpatterns = [
    path('payment/add/', PaymentView.as_view(), name='payment-add'),
]
