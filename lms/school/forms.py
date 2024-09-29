from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.urls import reverse
from django.utils.functional import lazy
from .models import Teacher, Student, Lesson, StudentProgress
from settings.models import Language
from users.models import User
from django.utils.translation import gettext_lazy as _


def get_language_choices():
    return Language.objects.all().values_list('id', 'name')


SCHOOL_ROLE_CHOICES = (
    ('None', _('None')),
    ('teacher', _('Teacher')),
    ('student', _('Student')),
)


class BaseUserForm(forms.ModelForm):
    language_choices = lazy(get_language_choices, list)
    language = forms.MultipleChoiceField(
        choices=language_choices,
        widget=forms.CheckboxSelectMultiple
    )

    username = forms.CharField(max_length=150, label=_("Username"))
    first_name = forms.CharField(max_length=30, label=_("First Name"))
    last_name = forms.CharField(max_length=30, label=_("Last Name"))
    email = forms.EmailField(label=_("Email"))

    school_role = forms.ChoiceField(
        choices=SCHOOL_ROLE_CHOICES,
        label=_("School Role"),
        help_text=_("Choose school role (teacher или student)."),
        required=True,
    )

    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput,
        help_text=_("""Your password can’t be too similar to your other personal information.<br>
                    Your password must contain at least 8 characters.<br>
                    Your password can’t be a commonly used password.<br>
                    Your password can’t be entirely numeric."""),
        required=False
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput,
        help_text=_("Repeat password."),
        required=False
    )

    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_("You can change the password using."),
        required=False
    )

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.initial['language'] = list(self.instance.language.values_list('id', flat=True))
            user_instance = self.instance.user
            if user_instance:
                self.fields['username'].initial = user_instance.username
                self.fields['first_name'].initial = user_instance.first_name
                self.fields['last_name'].initial = user_instance.last_name
                self.fields['email'].initial = user_instance.email
                self.fields['school_role'].initial = user_instance.school_role

                self.fields['password1'].initial = ''
                self.fields['password2'].initial = ''
                self.fields['password'].initial = user_instance.password

                password_change_url = reverse('admin:auth_user_password_change', args=[user_instance.pk])
                self.fields['password'].help_text = _("You can change the password using <a href='{password_change_url}'>this form</a>.").format(password_change_url=password_change_url)
        else:
            self.fields['password'].initial = ""
            self.fields['password1'].required = True
            self.fields['password2'].required = True

    def save_user(self, user_instance):
        user_instance.username = self.cleaned_data['username']
        user_instance.first_name = self.cleaned_data['first_name']
        user_instance.last_name = self.cleaned_data['last_name']
        user_instance.email = self.cleaned_data['email']
        user_instance.school_role = self.cleaned_data['school_role']
        user_instance.set_password(self.cleaned_data['password1'])
        user_instance.save()

class TeacherForm(BaseUserForm):
    class Meta(BaseUserForm.Meta):
        model = Teacher
        fields = '__all__'
        widgets = {
            'user': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['school_role'].initial = 'teacher'

    def save(self, commit=True):
        teacher = super().save(commit=False)

        if not teacher.user:
            user = User()
            self.save_user(user)
            teacher.user = user
        else:
            self.save_user(teacher.user)

        if commit:
            teacher.save()
        return teacher


class StudentForm(BaseUserForm):
    class Meta(BaseUserForm.Meta):
        model = Student
        fields = '__all__'
        widgets = {
            'user': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['school_role'].initial = 'student'

    def save(self, commit=True):
        student = super().save(commit=False)

        if not student.user:
            user = User()
            self.save_user(user)
            student.user = user
        else:
            self.save_user(student.user)

        if commit:
            student.save()
        return student


class LessonForm(forms.ModelForm):
    def __init__(self, teacher, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['students'].queryset = Student.objects.filter(teacher=teacher, user__is_active=True)
        self.fields['teacher'].initial = teacher

    class Meta:
        model = Lesson
        fields = ('date', 'time', 'duration', 'students', 'teacher', 'theme', 'notes', 'homework')
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date'
            }),
            'time': forms.TextInput(attrs={
                'type': 'text',
                'class': 'time-mask',
                'value': '',
                'placeholder': 'HH:mm',
                'list': 'time-options'
            }),
            'notes': forms.HiddenInput(),
            'homework': forms.HiddenInput(),
            'teacher': forms.HiddenInput()
        }


class LessonMoveForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ('date', 'time')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TextInput(attrs={
                'type': 'text',
                'class': 'time-mask',
                'value': '',
                'placeholder': 'HH:mm',
                'list': 'time-options'
            }),
        }


class ProgressStageForm(forms.ModelForm):
    def __init__(self, student, teacher, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].initial = student
        self.fields['teacher'].initial = teacher

    class Meta:
        model = StudentProgress
        fields = ('title', 'description', 'student', 'teacher')
        widgets = {
            'student': forms.HiddenInput(),
            'teacher': forms.HiddenInput()
        }


class UserCommonForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class TeacherCommonForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['about']


class UserCombineCommonForm(forms.Form):
    username = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    about = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        teacher = kwargs.pop('teacher', None)
        super(UserCombineCommonForm, self).__init__(*args, **kwargs)

        if user:
            self.fields['username'].initial = user.username
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

        if teacher:
            self.fields['about'].initial = teacher.about
        else:
            self.fields.pop('about')

    def save(self, user, teacher=None):
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.save()

        if teacher:
            teacher.about = self.cleaned_data['about']
            teacher.save()


class UserChangePassword(forms.ModelForm):
    old_password = forms.CharField(widget=forms.PasswordInput())
    new_password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(UserChangePassword, self).__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            self.add_error('old_password', "Incorrect password")
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            self.add_error('confirm_password', "Passwords must match")

        return cleaned_data

    def save(self, commit=True):
        user = self.user
        user.set_password(self.cleaned_data['new_password'])
        if commit:
            user.save()
        return user
