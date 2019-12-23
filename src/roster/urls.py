from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from roster.views import HomeView, TeamRosterView


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('<str:slug>/', TeamRosterView.as_view(), name='team-roster')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
