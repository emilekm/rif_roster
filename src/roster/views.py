from itertools import groupby

from django.views.generic import DetailView, ListView
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from guardian.shortcuts import get_objects_for_user, get_perms

from roster.models import Squad, Team


class NavbarMixin:
    def get(self, request, *args, **kwargs):
        self.request = request
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Little tricky here, weird thing with global vs obj perms
        teams = Team.objects.all()
        context['teams'] = [team for team in teams if self.request.user.has_perm('roster.view_team', team)]
        return context


class HomeView(LoginRequiredMixin, NavbarMixin, ListView):
    template_name = 'roster/home.html'
    model = Team

    def get(self, request, *args, **kwargs):
        self.object_list = get_objects_for_user(self.request.user, 'roster.view_team', klass=self.model)
        if len(self.object_list) < 1:
            return super().get(request, *args, **kwargs)
        return redirect(reverse('team-roster', kwargs={'slug': self.object_list[0].slug}))



class TeamRosterView(LoginRequiredMixin, NavbarMixin, DetailView):
    model = Team
    template_name = 'roster/roster.html'
    query_pk_and_slug = True

    def get_object(self, queryset=None):
        obj = super().get_object()
        if self.request.user.has_perm('roster.view_team', obj):
            return obj
        self.handle_no_permission()

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
