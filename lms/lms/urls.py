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


urlpatterns = i18n_patterns(
    path("i18n/", include("django.conf.urls.i18n")),
    path('admin/', admin.site.urls, name='admin'),
    path('', include('users.urls')),
    path('', include('school.urls')),
    path('', include('faq.urls')),
    path('', include('pages.urls')),
    path('', include('siteapp.urls')),
    path('django_ckeditor_5/', include('django_ckeditor_5.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
