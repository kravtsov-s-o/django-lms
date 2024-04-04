from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import MyUserCreationForm, MyUserChangeForm


# Register your models here.
@admin.register(User)
class MyUserAdmin(UserAdmin):
    model = User
    add_form = MyUserCreationForm
    form = MyUserChangeForm

    add_fieldsets = (
        *UserAdmin.add_fieldsets,
        (
            'Custom fields',
            {
                'fields': (
                    'first_name',
                    'last_name',
                    'email',
                    'school_role',
                    'groups'
                )
            }
        )
    )

    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'Custom fields',
            {
                'fields': (
                    'school_role',
                )
            }
        )
    )