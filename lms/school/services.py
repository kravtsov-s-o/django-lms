import calendar
import operator
from datetime import datetime
from collections import defaultdict

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models.functions import ExtractYear
from django.shortcuts import get_object_or_404
from decimal import Decimal

from .models import Student, Teacher, Lesson
from companies.models import Company
from settings.models import Currency, Duration
from transactions.models import Price, TransactionType, StudentPayment, TeacherPayment, CompanyPayment

from functools import wraps
from django.core.exceptions import PermissionDenied

from django.utils.translation import gettext_lazy as _

# IN PERCENTS %
GROUP_DISCOUNT = {
    1: 0,
    2: 10,
    3: 15,
    4: 20,
}


def get_default_system_currency() -> Currency:
    """
    Return Base Currency from settings
    """
    return get_object_or_404(Currency, is_default=True)


def get_default_lesson_length() -> Duration:
    """
    Return Base Duration from settings
    """
    return int(get_object_or_404(Duration, is_default=True).time)


def get_outgoing_lesson_transaction_type():
    """
    Returns the transaction type for outgoing lessons.
    Using for Students and companies

    Returns
    -------
        TransactionType
    """
    return TransactionType.objects.filter(type='outgoing', is_system=True).first()


def get_incoming_lesson_transaction_type():
    """
    Returns the transaction type for outgoing lessons.
    Using for Teachers

    Returns
    -------
        TransactionType
    """
    return TransactionType.objects.filter(type='incoming', is_system=True).first()


def get_rate_price(plan: Price):
    """
    Return price from rate

    return rate or rate with discount
    """
    percents = 100

    if plan.discount:
        return plan.price * ((percents - plan.discount) / percents)

    return plan.price


# =================================================================

def calculate_price(rate: Decimal, duration: int) -> Decimal:
    """
    Calculate base lesson price

    Parameters
    ----------
        rate: user rate
        duration: lesson duration
        number_of_students: students on lesson

    Returns
    -------
        lesson price
    """
    price = rate * Decimal(duration / get_default_lesson_length())
    return round(price, 2)


def calculate_teacher_price(teacher: Teacher, lesson: Lesson, number_of_students: int) -> Decimal:
    """
    Calculates the price for teacher

    Use Teacher rate and currency. If teacher rate 0, using full lesson price.
    Convert lesson price to teacher currency

    Parameters
    ----------
        teacher: Teacher object
        duration: lesson duration
        lesson: Lesson object
        number_of_students: students on lesson

    Returns
    -------
        lesson price
    """
    teacher_rate = get_rate_price(teacher.price_plan)

    if teacher_rate == 0:
        lesson_price = lesson.price

        if lesson.currency != teacher.price_plan.currency:
            if lesson.currency != get_default_system_currency():
                lesson_price /= lesson.currency.exchange

            lesson_price /= teacher.price_plan.currency.exchange

        return round(lesson_price, 2)

    return calculate_price(teacher_rate, lesson.duration.time) * number_of_students


# =================================================================
def get_lesson_currency(students: list) -> Currency:
    """
    Check lesson currency, base on students currency or students company currency.
    If Student shave different currencies, use system default currency
    """
    if get_students_company(students):
        return get_students_company(students).price_plan.currency
    elif check_students_currencies(students):
        return check_students_currencies(students)
    else:
        return get_default_system_currency()


# =================================================================

def check_students_currencies(students: list[Student]) -> Currency | None:
    """
    Check if all students from one lesson have one currency

    Returns
    currency: Currency | None
    """
    if all(student.price_plan.currency for student in students) and len(
            {student.price_plan.currency for student in students}) == 1:
        return students[0].price_plan.currency

    return None


def get_students_company(students: list[Student]) -> Company | None:
    """
    Check if all students from one company.
    :param students: список учеников на уроке
    :return: Компания или None
    """
    if all(student.company for student in students) and len({student.company for student in students}) == 1:
        return students[0].company

    return None


def set_student_transaction_for_lesson(student: Student, price, transaction_type=None, operator_symbol='-',
                                       lesson: Lesson = None):
    """
    Set transaction for student

    Parameters
    ----------
        student - the student object
        lesson - the lesson object
        company - the company object
    """
    operators = {
        '+': operator.add,
        '-': operator.sub,
    }

    if transaction_type is None:
        transaction_type = get_outgoing_lesson_transaction_type()
    StudentPayment(lesson=lesson, price=price, transaction_type=transaction_type, student=student).save()
    student.wallet = operators[operator_symbol](student.wallet, price)
    student.save()


def set_company_transaction(company: Company, price, transaction_type=None, operator_symbol='-', lesson: Lesson = None):
    """
    Set transaction for company

    Parameters
    ----------
        company - the company object
        lesson - the lesson object
    """
    operators = {
        '+': operator.add,
        '-': operator.sub,
    }

    if transaction_type is None:
        transaction_type = get_outgoing_lesson_transaction_type()
    CompanyPayment(lesson=lesson, price=price, transaction_type=transaction_type, company=company).save()
    company.wallet = operators[operator_symbol](company.wallet, price)
    company.save()


def set_teacher_transaction(teacher: Teacher, lesson: Lesson, price):
    """
    Set transaction for teacher

    Parameters
    ----------
        teacher - the teacher object
        lesson - the lesson object
    """
    transaction_type = get_incoming_lesson_transaction_type()
    TeacherPayment(lesson=lesson, price=price, transaction_type=transaction_type, teacher=teacher).save()


def back_money_for_back_lesson_to_status_planned(transaction):
    item = transaction.company
    item.wallet += transaction.price
    item.save()
    transaction.delete()


def lesson_pay_back(lesson: Lesson, status: str, company: Company):
    """
    Back Money for canceled lesson, delete relation transactions
    """
    lesson.price = 0
    lesson.currency = None
    lesson.status = status

    lesson.save()

    teacher_transaction = get_object_or_404(TeacherPayment, lesson=lesson)
    teacher_transaction.delete()

    if company:
        company_transaction = get_object_or_404(CompanyPayment, lesson=lesson)
        company = company_transaction.company
        company.wallet += company_transaction.price
        company.save()
        company_transaction.delete()

    student_transactions = StudentPayment.objects.filter(lesson=lesson)
    for student_transaction in student_transactions:
        student = student_transaction.student
        student.wallet += student_transaction.price
        student.save()
        student_transaction.delete()


def lesson_finished(teacher: Teacher, lesson_id: int, status: str):
    """
    Marks the given lesson as finished and calculates the final price based on the lesson duration,
    number of students, and the availability of a company.
    Generate Transactions for Teacher, Student(s), Company(Option)

    Parameters
    ----------
        teacher - the teacher object
        lesson_id - the ID of the lesson
        status - the new status of the lesson ("conducted", "missed", "planned")
    """
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    lesson_students = lesson.students.all()
    lesson_currency = get_lesson_currency(lesson_students)
    teacher = lesson.teacher
    group_discount = Decimal(1 - GROUP_DISCOUNT[len(lesson_students)] / 100)
    company = get_students_company(lesson_students)
    company_discount = Decimal(1 - company.discount / 100) if company else 1

    if status == Lesson.LessonStatus.PLANNED:
        lesson_pay_back(lesson, status, company)
        return

    status_set = {Lesson.LessonStatus.CONDUCTED, Lesson.LessonStatus.MISSED}
    if lesson.status in status_set and status in status_set and lesson.status != status:
        lesson.status = status
        lesson.save()
        return

    lesson_price = 0
    company_price = 0
    student_prices = {}
    if 0 < company_discount <= 1:
        for student in lesson_students:
            price = calculate_price(get_rate_price(student.price_plan), lesson.duration.time)
            if 0 < group_discount < 1:
                price *= group_discount
            if 0 < company_discount < 1:
                price *= group_discount

            student_prices[student] = price

            if check_students_currencies(lesson_students) is None:
                price /= student.price_plan.currency.exchange

            lesson_price += price
    else:
        for student in lesson_students:
            student_prices[student] = 0

    if company:
        company_price = calculate_price(get_rate_price(company.price_plan), lesson.duration.time) * len(
            lesson_students) * Decimal((company.discount / 100))
        if 0 < group_discount < 1:
            company_price *= group_discount
        lesson_price += company_price

    lesson.status = status
    lesson.price = lesson_price
    lesson.currency = lesson_currency
    lesson.save()

    # Teacher Price
    teacher_price = calculate_teacher_price(teacher, lesson, len(lesson_students))
    set_teacher_transaction(teacher, lesson, teacher_price)

    # Company Price
    if company:
        set_company_transaction(company, lesson, company_price)

    # Student(s) Price
    for student in lesson_students:
        set_student_transaction_for_lesson(student, lesson, student_prices[student])


# =================================================================
def user_is_student_or_teacher(view_func):
    """
    Check user rights Teacher or Student
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if user.school_role == 'student':
            profile = get_object_or_404(Student, user=user)
        elif user.school_role == 'teacher':
            profile = get_object_or_404(Teacher, user=user)

        if request.user == profile.user or (hasattr(profile, 'teacher') and profile.teacher.user == request.user):
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return _wrapped_view


def user_is_teacher(view_func):
    """
    Check user rights Teacher
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        pk = kwargs.get('pk')

        if request.user.school_role == 'teacher' and request.user.id == pk:
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return _wrapped_view


def user_is_student_teacher(view_func):
    """
    Check user is Student Teacher
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        student_pk = kwargs.get('pk')
        student = get_object_or_404(Student, pk=student_pk)

        if request.user == student.teacher.user:
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return _wrapped_view


def user_is_lesson_teacher(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        lesson_pk = kwargs.get('pk')
        lesson = get_object_or_404(Lesson, pk=lesson_pk)

        if request.user.school_role == 'teacher' and request.user.id == lesson.teacher.user.id:
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return _wrapped_view


def user_is_staff(view_func):
    """
    Check user rights in Admin
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return _wrapped_view


def count_time_left(user):
    """
    Count time left for user to paid for lesson

    Returns
    -------
        string: time left in format '10 hour(s) 30 minutes'
    """
    if user.wallet <= 0:
        return _('0 hour(s)')
    time_left = user.wallet / user.price_plan.price
    hours = int(time_left)
    minutes = int((time_left - hours) * 60)
    return _("{hours} hour(s) {minutes} minutes").format(hours=hours, minutes=minutes)


def get_paginator(items, items_per_page, request, surrounding=2):
    """
    Cut items per page

    Parameters
    ----------
        items: list of items
        items_per_page: number of items per page
        request: current request object

    Returns
    -------
        items_page: Paginated items
        page_range: Range of pages
    """
    paginator = Paginator(items, items_per_page)

    page = request.GET.get("page")

    try:
        items_page = paginator.page(page)
    except PageNotAnInteger:
        items_page = paginator.page(1)
    except EmptyPage:
        items_page = paginator.page(paginator.num_pages)

    page_number = items_page.number
    total_pages = items_page.paginator.num_pages
    page_range = []

    min_page_range_threshold = surrounding + 1
    min_page_ellipsis_threshold = surrounding + 2
    max_page_ellipsis_threshold = surrounding - 1

    if page_number > min_page_range_threshold:
        page_range.append(1)
        if page_number > min_page_ellipsis_threshold:
            page_range.append('...')

    start_range = max(1, page_number - surrounding)
    end_range = min(total_pages, page_number + surrounding) + 1
    page_range.extend(range(start_range, end_range))

    if page_number < total_pages - surrounding:
        if page_number < total_pages - max_page_ellipsis_threshold:
            page_range.append('...')
        page_range.append(total_pages)

    return items_page, page_range


def get_teacher(request):
    """
    Get teacher object by request user

    Returns
    -------
        Teacher: teacher object or None if not found
    """
    return Teacher.objects.filter(user=request.user).first()


def get_duration_list():
    """
    Get duration list from settings

    Returns
    -------
        list: list of Duration objects
    """
    return Duration.objects.all().order_by('time')


def generate_month_list_for_filter():
    month_list = [
        {
            'title': _(calendar.month_name[i]),
            'number': i
        }
        for i in range(1, 13)
    ]

    return month_list


def get_year_list(model, field='created_at', default=datetime.today().year):
    years_list = (model.objects
                  .annotate(year=ExtractYear(field))
                  .values_list('year', flat=True).distinct().order_by('year'))

    if not years_list:
        return [default]

    return years_list


def sort_data_for_analytics(data):
    """
    Sort data for analytics pages

    Parameters
    ----------
        data QuerySet from DataBase

    Results
    -------
        list: Sorted data for analytics pages
    """
    queryset = []
    for lesson in data:
        lesson_students = (Lesson
                           .objects
                           .filter(pk=lesson["lesson__id"])
                           .values_list('students__user__first_name', 'students__user__last_name'))

        item = {
            'lesson_id': lesson["lesson__id"],
            'students': ', '.join([f"{first_name} {last_name}" for first_name, last_name in lesson_students]),
            'duration': lesson["lesson__duration__time"],
        }

        queryset.append(item)

    combined_data = defaultdict(lambda: {"students": "", "duration": 0, "count": 0})

    for entry in queryset:
        key = (entry["students"], entry["duration"])
        if combined_data[key]["students"] == "":
            combined_data[key]["students"] = entry["students"]
            combined_data[key]["duration"] = entry["duration"]
        combined_data[key]["count"] += 1

    return list(combined_data.values())
