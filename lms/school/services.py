import calendar
from collections import defaultdict

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models.functions import ExtractYear
from django.shortcuts import get_object_or_404
from decimal import Decimal

from .models import Student, Teacher, Lesson
from companies.models import Company
from settings.models import Currency, Duration
from transactions.models import StudentPayment, TeacherPayment, CompanyPayment

from functools import wraps
from django.core.exceptions import PermissionDenied

DEFAULT_LESSON_DURATION = 60  # minutes
GROUP_DISCOUNT = {
    1: Decimal(1),
    2: Decimal(0.9),
    3: Decimal(0.85),
    4: Decimal(0.8),
}


def payment_description(lesson: Lesson) -> str:
    """
    Returns a description for the payment related to the given lesson.

    Parametrs
    -------
        lesson - the lesson object

    Returns
    -------
        string - description for the payment related to the given lesson
    """
    students = ', '.join(
        [f'{student.user.first_name} {student.user.last_name}' for student in lesson.students.all()])
    date = lesson.date.strftime("%d.%m.%Y")
    time = lesson.time.strftime("%H:%M")
    return f"For lesson {date} - {time}; Students: {students}"


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

    Raises
    ------
        PermissionDenied - if the user is not the teacher of the lesson

    if teacher != lesson.teacher:
        raise PermissionDenied("You are not the teacher of this lesson.")

    lesson_finished_service(teacher, lesson_id, status)
    """
    lesson = get_object_or_404(Lesson, pk=lesson_id, teacher=teacher)
    company = get_students_company(lesson.students.all())

    if status == 'planned':
        lesson_pay_back(lesson, status, company)
    else:

        lesson.status = status
        lesson.price = calculate_lesson_price(lesson.duration.time, lesson.students.all(), company)
        lesson.currency = set_lesson_currency(lesson.students.all())

        lesson.save()

        # Teacher Price
        set_teacher_transaction(teacher, lesson)

        # Company Price
        if company:
            set_company_transaction(company, lesson)

        # Student(s) Price
        for student in lesson.students.all():
            set_student_transaction(student, lesson, company)


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


def set_company_transaction(company: Company, lesson: Lesson):
    """
    Set transaction for company

    Parameters
    ----------
        company - the company object
        lesson - the lesson object
    """
    duration = lesson.duration.time
    number_of_students = len(lesson.students.all())
    price = calculate_company_price(company, duration, number_of_students)
    description = payment_description(lesson)
    CompanyPayment(lesson=lesson, price=price, description=description, company=company).save()
    company.wallet -= price
    company.save()


def set_teacher_transaction(teacher: Teacher, lesson: Lesson):
    """
    Set transaction for teacher

    Parameters
    ----------
        teacher - the teacher object
        lesson - the lesson object
    """
    duration = lesson.duration.time
    number_of_students = len(lesson.students.all())
    price = calculate_teacher_price(teacher, duration, lesson, number_of_students)
    description = payment_description(lesson)
    TeacherPayment(lesson=lesson, price=price, description=description, teacher=teacher).save()


def set_student_transaction(student: Student, lesson: Lesson, company: Company):
    """
    Set transaction for student

    Parameters
    ----------
        student - the student object
        lesson - the lesson object
        company - the company object
    """
    duration = lesson.duration.time
    number_of_students = len(lesson.students.all())
    price = calculate_student_price(student.rate, duration, number_of_students, company)
    description = payment_description(lesson)
    StudentPayment(lesson=lesson, price=price, description=description, student=student).save()
    student.wallet -= price
    student.save()


def get_default_system_currency() -> Currency:
    """
    Return Base Currency from settings
    """
    return get_object_or_404(Currency, default=True)


def check_students_currencies(students: list[Student]) -> Currency | None:
    """
    Check if all students from one lesson have one currency

    Returns
    currency: Currency | None
    """
    if all(student.currency for student in students) and len({student.currency for student in students}) == 1:
        return students[0].currency

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


def calculate_lesson_price(duration: int, students: list, company: Company = None) -> Decimal:
    """
    Calculate lesson Price
    :param duration: lesson Duration
    :param students: students
    :param company: company, default = None
    :return: lesson price
    """
    number_of_students = len(students)

    if company:
        return calculate_company_price(company, duration, number_of_students)

    lesson_price = Decimal(0)
    if check_students_currencies(students):
        for student in students:
            lesson_price += calculate_price(student.rate, duration, number_of_students)
    else:
        for student in students:
            lesson_price += calculate_price(student.rate, duration, number_of_students) / student.currency.exchange

    return lesson_price


def set_lesson_currency(students: list) -> Currency:
    """
    Set lesson currency, base on students currency or students company.
    If Student shave different currencies, use system default currency
    """
    if get_students_company(students):
        return get_students_company(students).currency
    elif check_students_currencies(students):
        return check_students_currencies(students)
    else:
        return get_default_system_currency()


def calculate_price(rate: Decimal, duration: int, number_of_students: int) -> Decimal:
    """
    Calculate base lesson price

    Parametrs
    ----------
        rate: user rate
        duration: lesson duration
        number_of_students: students on lesson

    Returns
    -------
        lesson price
    """
    group_discount = GROUP_DISCOUNT[4] if number_of_students >= 4 else GROUP_DISCOUNT[number_of_students]
    price = rate * Decimal(duration / DEFAULT_LESSON_DURATION) * group_discount
    return round(price, 2)


def calculate_student_price(rate: Decimal, duration: int, number_of_students: int, company=None) -> Decimal:
    """
    Calculate lesson price for each student

    Parametrs
    ----------
        rate: user rate
        duration: lesson duration
        number_of_students: students on lesson
        company: if company pay for student user Company discount

    Returns
    -------
        lesson price
    """
    if company:
        discount = Decimal(1 - (company.discount / 100))
        rate *= discount

    price = calculate_price(rate, duration, number_of_students)
    return price


def calculate_company_price(company: Company, duration: int, number_of_students: int) -> Decimal:
    """
    Calculate lesson price when company pay for their workers

    Parametrs
    ----------
        company: Company object
        duration: lesson duration
        number_of_students: students on lesson

    Returns
    -------
        lesson price
    """
    company_discount = Decimal(company.discount / 100)  # Переводим % в дробь: 100 = 1; 50 = 0.5
    company_rate = company.rate if company_discount == 1 else (company.rate * company_discount)

    company_price = calculate_price(company_rate, duration, number_of_students) * number_of_students

    return company_price


def calculate_teacher_price(teacher: Teacher, duration: int, lesson: Lesson, number_of_students: int) -> Decimal:
    """
    Calculates the price for teacher

    Use Teacher rate and currency. If teacher rate 0, using full lesson price.
    Convert lesson price to teacher currency

    Parametrs
    ----------
        teacher: Teacher object
        duration: lesson duration
        lesson: Lesson object
        number_of_students: students on lesson

    Returns
    -------
        lesson price
    """
    teacher_rate = teacher.rate

    if not teacher_rate:
        lesson_price = lesson.price

        if lesson.currency != teacher.currency:
            if lesson.currency != get_default_system_currency():
                lesson_price /= lesson.currency.exchange

            lesson_price /= teacher.currency.exchange

        return round(lesson_price, 2)

    return calculate_price(teacher_rate, duration, number_of_students) * number_of_students


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
        return '0 hour(s)'
    time_left = user.wallet / user.rate
    hours = int(time_left)
    minutes = int((time_left - hours) * 60)
    return f"{hours} hour(s) {minutes} minutes"


def get_paginator(items, items_per_page, request):
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

    page_range = range(1, items_page.paginator.num_pages + 1)

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
    return Duration.objects.all()


def generate_month_list_for_filter():
    month_list = [
        {
            'title': calendar.month_name[i],
            'number': i
        }
        for i in range(1, 13)
    ]

    return month_list


def get_year_list(model, field='created_at'):
    return (model.objects
                       .annotate(year=ExtractYear(field))
                       .values_list('year', flat=True).distinct().order_by('year'))


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
