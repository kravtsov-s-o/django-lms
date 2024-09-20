from django.shortcuts import get_object_or_404
from decimal import Decimal

from .models import Student, Teacher, Lesson
from companies.models import Company
from settings.models import Currency, Duration
from transactions.models import StudentPayment, TeacherPayment, CompanyPayment

# =================================================================
from functools import wraps
from django.core.exceptions import PermissionDenied
from users.models import User

# =================================================================

DEFAULT_LESSON_DURATION = 60  # minutes
GROUP_DISCOUNT = {
    1: Decimal(1),
    2: Decimal(0.9),
    3: Decimal(0.85),
    4: Decimal(0.8),
}


def payment_description(lesson):
    students = ', '.join(
        [f'{student.user.first_name} {student.user.last_name}' for student in lesson.students.all()])
    date = lesson.date.strftime("%d.%m.%Y")
    time = lesson.time.strftime("%H:%M")
    return f"For lesson {date} - {time}; Students: {students}"


def lesson_finished(teacher, lesson_id, status):
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


def lesson_pay_back(lesson, status, company):
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


def set_company_transaction(company, lesson):
    duration = lesson.duration.time
    number_of_students = len(lesson.students.all())
    price = calculate_company_price(company, duration, number_of_students)
    student_names = ', '.join(
        [f'{student.user.first_name} {student.user.last_name}' for student in lesson.students.all()])
    description = payment_description(lesson)
    CompanyPayment(lesson=lesson, price=price, description=description, company=company).save()
    company.wallet -= price
    company.save()


def set_teacher_transaction(teacher, lesson):
    duration = lesson.duration.time
    number_of_students = len(lesson.students.all())
    price = calculate_teacher_price(teacher, duration, lesson, number_of_students)
    description = payment_description(lesson)
    TeacherPayment(lesson=lesson, price=price, description=description, teacher=teacher).save()


def set_student_transaction(student, lesson, company):
    duration = lesson.duration.time
    number_of_students = len(lesson.students.all())
    price = calculate_student_price(student.rate, duration, number_of_students, company)
    description = payment_description(lesson)
    StudentPayment(lesson=lesson, price=price, description=description, student=student).save()
    student.wallet -= price
    student.save()


def get_default_system_currency() -> Currency:
    return get_object_or_404(Currency, default=True)


def check_students_currencies(students):
    if all(student.currency for student in students) and len({student.currency for student in students}) == 1:
        return students[0].currency

    return None


def get_students_company(students) -> Company | None:
    """
    Проверяем чтобы у всех учеников была 1 компания.
    :param students: список учеников на уроке
    :return: Компания или None
    """
    if all(student.company for student in students) and len({student.company for student in students}) == 1:
        return students[0].company

    return None


def calculate_lesson_price(duration: int, students, company: Company = None):
    """
    Считаем цену урока
    :param duration: длительность урока
    :param students: студенты
    :param company: Компания если есть
    :return: Цена урока
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


def set_lesson_currency(students):
    if get_students_company(students):
        return get_students_company(students).currency
    elif check_students_currencies(students):
        return check_students_currencies(students)
    else:
        return get_default_system_currency()


def calculate_price(rate: Decimal, duration: int, number_of_students: int) -> Decimal:
    """
    Считаем цену на основе ставки, длительности урока и кол-ва студентов
    :param rate:
    :param duration:
    :param number_of_students:
    :return:
    """
    group_discount = GROUP_DISCOUNT[4] if number_of_students >= 4 else GROUP_DISCOUNT[number_of_students]
    price = rate * Decimal(duration / DEFAULT_LESSON_DURATION) * group_discount
    return round(price, 2)


def calculate_student_price(rate: Decimal, duration: int, number_of_students: int, company=None):
    if company:
        discount = Decimal(1 - (company.discount / 100))
        rate *= discount

    price = calculate_price(rate, duration, number_of_students)
    return price


def calculate_company_price(company: Company, duration: int, number_of_students: int) -> Decimal:
    """
    Цена урока для каомпании, с учетом скидки ученикам от компании
    :param company:
    :param duration:
    :param number_of_students:
    :return: company_price
    """
    company_discount = Decimal(company.discount / 100)  # Переводим % в дробь: 100 = 1; 50 = 0.5
    company_rate = company.rate if company_discount == 1 else (company.rate * company_discount)

    company_price = calculate_price(company_rate, duration, number_of_students) * number_of_students

    return company_price


def calculate_teacher_price(teacher: Teacher, duration: int, lesson: Lesson, number_of_students: int) -> Decimal:
    """
    Расчет цены учителя с учетом стоимости занятия
    :param teacher:
    :param duration:
    :param lesson:
    :param number_of_students:
    :return:
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
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # profile_id = kwargs.get('pk')
        # user = get_object_or_404(User, pk=profile_id)
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


# =================================================================
def user_is_teacher(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Проверяем роль текущего пользователя
        if request.user.school_role == 'teacher':
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied  # Возвращаем ошибку 403, если не учитель

    return _wrapped_view
# =================================================================
def user_is_staff(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Проверяем роль текущего пользователя
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied  # Возвращаем ошибку 403, если не учитель

    return _wrapped_view


# =================================================================
# Time left
def count_time_left(user):
    if user.wallet <= 0:
        return '0 hour(s)'
    time_left = user.wallet / user.rate
    hours = int(time_left)
    minutes = int((time_left - hours) * 60)
    return f"{hours} hour(s) {minutes} minutes"
# =================================================================
