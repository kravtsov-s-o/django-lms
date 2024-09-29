from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import User


class MyUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = '__all__'

    def save(self, commit=True):
        # Перед сохранением добавляем флаг на экземпляре
        self.instance.is_from_user_form = True
        return super().save(commit)


class MyUserChangeForm(UserChangeForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = '__all__'

    def save(self, commit=True):
        # Перед сохранением добавляем флаг на экземпляре
        self.instance.is_from_user_form = True
        return super().save(commit)


class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ('username', 'password')
