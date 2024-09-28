from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.views import View
from .forms import LoginForm
from django.utils.translation import gettext_lazy as _


# Create your views here.
class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(to='school:profile-lessons', pk=request.user.id)

        form = LoginForm()
        return render(request, 'users/login.html', context={'title': 'Login', 'form': form})

    def post(self, request):
        user = authenticate(username=request.POST['username'], password=request.POST['password'])

        if not user:
            messages.error(request, _('Username or password didn\'t match'))
            return redirect(to='users:login')

        login(request, user)
        if request.user.school_role in ['None', 'none', None] and (request.user.is_staff or request.user.is_superuser):
            return redirect(to='admin:index')
        else:
            return redirect(to='school:profile-lessons', pk=request.user.id)
