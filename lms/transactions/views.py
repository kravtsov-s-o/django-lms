from itertools import chain

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages

from .forms import PaymentForm
from school.services import user_is_staff, set_student_transaction, set_company_transaction
from django.utils.translation import gettext_lazy as _

from .models import StudentPayment, CompanyPayment, TransactionType


# Create your views here.
@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_is_staff, name='dispatch')
class PaymentView(View):
    title = _('Add payment')

    def get_form(self, request=None):
        return PaymentForm(request)

    def get_last_transactions(self):
        last_student_transactions = list(StudentPayment.objects.filter(lesson=None).order_by('-created_at')[:10])
        last_company_transactions = list(CompanyPayment.objects.filter(lesson=None).order_by('-created_at')[:10])

        combined_transactions = list(chain(last_student_transactions, last_company_transactions))

        combined_transactions_sorted = sorted(combined_transactions, key=lambda x: x.created_at, reverse=True)

        final_transactions = combined_transactions_sorted[:10]

        return final_transactions

    def get(self, request):
        form = self.get_form()

        return render(request,
                      'transactions/payment-form.html',
                      context={
                          'title': self.title,
                          'form': form,
                          'current_page': 'payment-add',
                          'last_payments': self.get_last_transactions()
                      })

    def post(self, request):
        form = self.get_form(request=request.POST)

        if form.is_valid():
            price = form.cleaned_data.get('price')
            transaction_type = get_object_or_404(TransactionType, pk=form.cleaned_data.get('transaction_type'))
            user = ''

            if form.cleaned_data.get('payment_type') == 'student':
                student = form.cleaned_data.get('student')

                StudentPayment(lesson=None, price=price, transaction_type=transaction_type, student=student).save()
                student.wallet += price
                student.save()
                user = student

            elif form.cleaned_data.get('payment_type') == 'company':
                company = form.cleaned_data.get('company')

                CompanyPayment(lesson=None, price=price, transaction_type=transaction_type, company=company).save()
                company.wallet += price
                company.save()

                user = company

            messages.success(request, _('Payment for <b>{user}</b> added successfully.').format(user=user))
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            messages.error(request, _('Check form fields'))
            return render(request,
                          'transactions/payment-form.html',
                          context={
                              'title': self.title,
                              'form': form,
                              'current_page': 'payment-add',
                          })
