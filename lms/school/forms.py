from django import forms
from .models import Teacher, Student, Lesson, StudentProgress
from settings.models import Language
from users.models import User


class TeacherForm(forms.ModelForm):
    language_choices = Language.objects.all().values_list('id', 'name')
    language = forms.MultipleChoiceField(
        choices=language_choices,
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['language'] = list(self.instance.language.values_list('id', flat=True))

    class Meta:
        model = Teacher
        fields = '__all__'


class StudentForm(forms.ModelForm):
    language_choices = Language.objects.all().values_list('id', 'name')
    language = forms.MultipleChoiceField(
        choices=language_choices,
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['language'] = list(self.instance.language.values_list('id', flat=True))

    class Meta:
        model = Student
        fields = '__all__'


class LessonForm(forms.ModelForm):
    def __init__(self, teacher, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['students'].queryset = Student.objects.filter(teacher=teacher, user__is_active=True)
        self.fields['teacher'].initial = teacher

    class Meta:
        model = Lesson
        # fields = '__all__'
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
        fields = ['username', 'email',  'first_name', 'last_name']


class TeacherCommonFrom(forms.ModelForm):
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
