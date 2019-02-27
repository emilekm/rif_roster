from django.views.generic.list import ListView
from django.shortcuts import render

from roster.models import Squad


class SquadListView(ListView):
    model = Squad

