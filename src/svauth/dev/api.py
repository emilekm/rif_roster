from django.conf import settings

from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from .serializers import CustomAuthTokenSerializer


class LoginView(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        response.data['is_admin'] = token.user.is_staff
        return response


class LogoutView(APIView):
    def post(self, request):
        request.user.auth_token.delete()
        return Response()


class ProvidersListView(APIView):
    permission_classes = []

    def get(self, request):
        local_provider = {
            'name': 'local',
            'type': 'local'
        }
        providers = [local_provider] + [{'name': name, 'type': config['type']} for name, config in settings.AUTH_PROVIDERS.items()]
        return Response(providers)
