from django import template

register = template.Library()


def extract_languages(languages):
    return ', '.join([str(language) for language in languages.all()])


register.filter('extract_languages', extract_languages)
