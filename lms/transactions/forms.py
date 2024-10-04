from django import forms
from django.utils.translation import gettext_lazy as _
from school.models import Student
from companies.models import Company


class PaymentForm(forms.Form):
    PAYMENT_CHOICES = (
        ('student', _('Student Payment')),
        ('company', _('Company Payment')),
    )

    payment_type = forms.ChoiceField(choices=PAYMENT_CHOICES, label=_('Payment Type'),
        widget=forms.RadioSelect, initial='student')
    student = forms.ModelChoiceField(queryset=Student.objects.all(), required=False, label=_('Student'))
    company = forms.ModelChoiceField(queryset=Company.objects.all(), required=False, label=_('Company'))
    price = forms.DecimalField(max_digits=10, decimal_places=2, label=_('Total'))
    description = forms.CharField(max_length=255, required=False, label=_('Description'), initial=_('Wallet replenishment'))

    def clean(self):
        cleaned_data = super().clean()
        payment_type = cleaned_data.get("payment_type")

        if payment_type == 'student' and not cleaned_data.get("student"):
            raise forms.ValidationError(_("Student must be specified for Student Payment"))
        elif payment_type == 'company' and not cleaned_data.get("company"):
            raise forms.ValidationError(_("Company must be specified for Company Payment"))

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].label_from_instance = self.get_label_from_instance_students
        self.fields['company'].label_from_instance = self.get_label_from_instance_companies

    def get_label_from_instance_students(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name} - {obj.currency}"

    def get_label_from_instance_companies(self, obj):
        return f"{obj.name} - {obj.currency}"
