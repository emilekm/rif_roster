from django.urls import path

from roster.views import TeamRosterView


urlpatterns = [
    path('teams/<int:pk>/', TeamRosterView.as_view(), name='team-roster-view')
]
