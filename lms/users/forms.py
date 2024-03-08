from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        # fields = '__all__'
        fields = ('username', 'first_name', 'last_name', 'school_role', 'groups')


class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'
        # fields = ('username', 'first_name', 'last_name', 'school_role', 'groups')
