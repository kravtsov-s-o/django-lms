from django import template

register = template.Library()


def extract_languages(student_languages):
    return ', '.join([str(language) for language in student_languages.all()])


register.filter('extract_languages', extract_languages)
