from itertools import groupby

from django.views.generic import DetailView
from django.shortcuts import render

from roster.models import Squad, Team


class TeamRosterView(DetailView):
    model = Team
    template_name = 'roster/roster.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['squads'] = [
            (squad, [
                (rank, list(roles))
                for rank, roles in groupby(squad.players.through.objects.filter(squad=squad), lambda x: x.get_role_display())
            ])
            for squad in Squad.objects.all().filter(team=self.object)
        ]
        return context
