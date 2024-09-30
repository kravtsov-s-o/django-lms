from django.shortcuts import render


# Create your views here.
def custom_page_not_found_view(request, exception):
    context = {
        'code': 404,
        'title': "Page Not Found :(",
        'message': "We couldn't find the page you are looking for",
        'error': str(exception),
    }
    return render(request, "siteapp/error-pages/404.html", context, status=404)


def custom_server_error_view(request):
    context = {
        'code': 500,
        'title': "Something went wrong.",
        'message': "We already working on it.",
    }
    return render(request, 'siteapp/error-pages/500.html', context, status=500)


def custom_page_access_denied_view(request, exception):
    context = {
        'code': 403,
        'title': "Access Denied",
        'error': str(exception),
    }
    return render(request, 'siteapp/error-pages/403.html', context, status=403)
