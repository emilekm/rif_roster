from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from roster.models import Player, Squad, SquadRole


link = '<a href="{}">{}</a>'


class SquadRoleInline(admin.TabularInline):
    model = SquadRole
    extra = 0


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'get_squads')
    inlines = [
        SquadRoleInline
    ]

    def get_squads(self, obj):
        roles = obj.squads.through.objects.filter(player=obj)
        return format_html(' | '.join([
            link.format(
                reverse('admin:roster_squad_change', args=[r.squad.id]),
                r.get_ranked_squad()
            )
            for r in roles
        ]))
    get_squads.short_description = 'Squads'


@admin.register(Squad)
class SquadAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'get_players')
    inlines = [
        SquadRoleInline
    ]

    def get_players(self, obj):
        roles = obj.players.through.objects.filter(squad=obj)
        return format_html('<br>'.join([
            link.format(
                reverse('admin:roster_player_change', args=[r.player.id]),
                r.get_ranked_player()
            )
            for r in roles
        ]))
    get_players.short_description = 'Players'

@admin.register(SquadRole)
class SquadRoleAdmin(admin.ModelAdmin):
    list_display = ('squad', 'get_role_display', 'player', )
