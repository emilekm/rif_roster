from django.conf.urls import url

from . import api

urlpatterns = [
    url(r'^login/$', api.LoginView.as_view()),
    url(r'^logout/$', api.LogoutView.as_view()),
    url(r'^providers/$', api.ProvidersListView.as_view())
]
