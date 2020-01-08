from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, UsernameField
from django.contrib.auth.models import Permission

from . import models


class SVUserChangeForm(UserChangeForm):
    class Meta:
        model = models.User
        fields = '__all__'
        field_classes = {'username': UsernameField}


class SVUserCreationForm(UserCreationForm):
    class Meta:
        model = models.User
        fields = ("username",)
        field_classes = {'username': UsernameField}


class SVUserAdmin(UserAdmin):
    form = SVUserChangeForm
    add_form = SVUserCreationForm
    fieldsets = UserAdmin.fieldsets + (
        ('svauth', {'fields': ('xf_user_id',)},),
    )


admin.site.register(models.User, SVUserAdmin)
admin.site.register(Permission, admin.ModelAdmin)
