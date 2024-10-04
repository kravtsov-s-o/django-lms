from django import template
from django.contrib.messages import constants as message_constants

register = template.Library()


# Фильтр для заголовка Toast
@register.filter(name='toast_title')
def toast_title(level):
    return {
        message_constants.DEBUG: 'Debug',
        message_constants.INFO: 'Info',
        message_constants.SUCCESS: 'Success',
        message_constants.WARNING: 'Warning',
        message_constants.ERROR: 'Error',
    }.get(level, 'Info')
