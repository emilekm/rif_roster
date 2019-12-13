from django.contrib import admin
from django.contrib.admin.models import LogEntry

from guardian.admin import GuardedModelAdmin, GuardedModelAdminMixin

from roster.models import Tournament, Team, Squad, SquadRole


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in LogEntry._meta.get_fields()]


class SquadRoleInline(admin.TabularInline, GuardedModelAdminMixin):
    model = SquadRole
    extra = 0


@admin.register(Squad)
class SquadAdmin(admin.ModelAdmin):
    inlines = [
        SquadRoleInline
    ]
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        all_teams = Team.objects.all()
        user_teams = [
            team for team in all_teams
            if request.user.has_perm('tournament.view_team', team)
        ]
        return queryset.filter(team__in=user_teams)


class TeamInline(admin.TabularInline):
    model = Team
    extra = 0


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    inlines = [
        TeamInline
    ]


class SquadInline(admin.TabularInline):
    model = Squad
    extra = 0


@admin.register(Team)
class TeamAdmin(GuardedModelAdmin):
    inlines = [
        SquadInline
    ]
