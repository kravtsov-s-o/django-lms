"""
URL configuration for lms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.shortcuts import render


def custom_page_not_found_view(request, exception):
    context = {
        'code': 404,
        'title': "Page Not Found :(",
        'message': "We couldn't find the page you are looking for",
        'error': str(exception),
    }
    return render(request, "404.html", context, status=404)


def custom_server_error_view(request):
    context = {
        'code': 500,
        'title': "Something went wrong.",
        'message': "We already working on it.",
    }
    return render(request, '500.html', context, status=500)


def custom_page_access_denied_view(request, exception):
    context = {
        'code': 403,
        'title': "Access Denied",
        'error': str(exception),
    }
    return render(request, '403.html', context, status=403)


handler404 = 'lms.urls.custom_page_not_found_view'
handler403 = 'lms.urls.custom_page_access_denied_view'
handler500 = 'lms.urls.custom_server_error_view'

# urlpatterns = [
#                   path('admin/', admin.site.urls, name='admin'),
#                   path('', include('users.urls')),
#                   path('', include('school.urls')),
#                   path('', include('faq.urls')),
#                   path('', include('pages.urls')),
#                   path('django_ckeditor_5/', include('django_ckeditor_5.urls')),
#               ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns = i18n_patterns(
    path("i18n/", include("django.conf.urls.i18n")),
    path('admin/', admin.site.urls, name='admin'),
    path('', include('users.urls')),
    path('', include('school.urls')),
    path('', include('faq.urls')),
    path('', include('pages.urls')),
    path('django_ckeditor_5/', include('django_ckeditor_5.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
