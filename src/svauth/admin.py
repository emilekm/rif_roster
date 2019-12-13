from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, UsernameField
from django.utils.translation import gettext_lazy

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
        (gettext_lazy('svweb'), {'fields': ('provider', 'is_machine')}),
    )


class SVRemoteGroupAdmin(admin.ModelAdmin):
    list_display = ("provider", "remote_id", "local_group")
    list_filter = ("provider", "remote_id", "local_group")

    @staticmethod
    def provider(instance: models.RemoteGroup):
        return instance.provider

    @staticmethod
    def remote_id(instance: models.RemoteGroup):
        return instance.remote_id

    @staticmethod
    def local_group(instance: models.RemoteGroup):
        return instance.local_group


admin.site.register(models.User, SVUserAdmin)
admin.site.register(models.RemoteGroup, SVRemoteGroupAdmin)
admin.site.register(Permission, admin.ModelAdmin)
