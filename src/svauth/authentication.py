import datetime
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


TOKEN_EXPIRATION_TIME = datetime.timedelta(hours=2)


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)

        now = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)

        # Note: Machine user token shouldn't expire
        if not user.is_machine and token.created < now - TOKEN_EXPIRATION_TIME:
            token.delete()
            raise AuthenticationFailed('Token has expired')

        return user, token
