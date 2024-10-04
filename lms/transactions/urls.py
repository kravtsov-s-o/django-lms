from django.urls import path
from .views import PaymntView

app_name = 'transactions'

urlpatterns = [
    path('payment/add/', PaymntView.as_view(), name='payment-add'),
]
