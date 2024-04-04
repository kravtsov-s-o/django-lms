from django import template

register = template.Library()


def extract_students(lesson_students):
    return ', '.join([str(student) for student in lesson_students.all()])


register.filter('extract_students', extract_students)
