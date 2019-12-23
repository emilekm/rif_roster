from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy

from guardian.admin import GuardedModelAdmin, GuardedModelAdminMixin

from roster.models import Team, Squad, SquadRole


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in LogEntry._meta.get_fields()]


class SquadRoleInline(admin.TabularInline, GuardedModelAdminMixin):
    model = SquadRole
    extra = 6


@admin.register(Squad)
class SquadAdmin(admin.ModelAdmin):
    inlines = [
        SquadRoleInline
    ]

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'team':
            queryset = Team.objects.all()
            user_teams = [
                team.pk for team in queryset
                if request.user.has_perm('roster.view_team', team)
            ]
            kwargs['queryset'] = queryset.filter(pk__in=user_teams)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        all_teams = Team.objects.all()
        user_teams = [
            team for team in all_teams
            if request.user.has_perm('roster.view_team', team)
        ]
        return queryset.filter(team__in=user_teams)


class SquadInline(admin.TabularInline):
    model = Squad
    extra = 2
    readonly_fields = ('change_link',)

    def change_link(self, obj):
        return format_html('<a href="{}">Members</a>'.format(
            reverse('admin:roster_squad_change', args=[obj.id])
        ))


@admin.register(Team)
class TeamAdmin(GuardedModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    inlines = [
        SquadInline,
    ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        user_teams = [
            team.pk for team in queryset
            if request.user.has_perm('roster.view_team', team)
        ]
        return queryset.filter(pk__in=user_teams)
