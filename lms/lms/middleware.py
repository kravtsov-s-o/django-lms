from django.conf import settings
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

class AppendSlashMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not settings.APPEND_SLASH:
            return
        if '/admin' in request.path or request.path.endswith('/'):
            return
        if not request.path_info.endswith('/'):
            return redirect(request.path_info + '/', permanent=True)
