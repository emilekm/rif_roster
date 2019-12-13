from django.conf.urls import include, url
from svweb_project.settings import CONFIG

app_name = 'svauth'

available = {
    "dev": [url(r'^dev/', include('svauth.dev.urls'))],
}

urlpatterns = []

select = [item for item in CONFIG.get("select_auth_versions", "").split(',') if item]
for patterns in (available[item] for item in select):
    urlpatterns += patterns
