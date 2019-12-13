from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer


class CustomAuthTokenSerializer(AuthTokenSerializer):
    provider = serializers.CharField(label=_("Provider"), default=None)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        provider = attrs.get('provider')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password, provider=provider)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
