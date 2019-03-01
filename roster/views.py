from itertools import groupby

from django.views.generic.list import ListView
from django.shortcuts import render

from roster.models import Squad


class SquadListView(ListView):
    model = Squad

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['squads'] = [
            (squad, [
                (rank, list(roles))
                for rank, roles in groupby(squad.players.through.objects.filter(squad=squad), lambda x: x.get_role_display())
            ])
            for squad in self.object_list
        ]
        return context


