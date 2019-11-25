from django.urls import path

from roster.views import SquadListView


urlpatterns = [
    path('', SquadListView.as_view(), name='squad-list-view')
]
