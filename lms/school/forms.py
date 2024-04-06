from django import forms
from .models import Teacher, Student, Lesson
from settings.models import Language


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
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            'notes': forms.HiddenInput(),
            'homework': forms.HiddenInput(),
            'teacher': forms.HiddenInput()
        }

class LessonMoveForm(forms.ModelForm):
    class Meta:
        model = Lesson
        # fields = '__all__'
        fields = ('date', 'time')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M')
        }
