from django.db import connections
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Group
from django.conf import settings

from svauth.models import Provider

from svauth.utils import dictfetchall, convert_to_django_password

UserModel = get_user_model()



class AuthProvider:
    def __init__(self, name, type, db_prefix, database):
        self.name = name
        self.type = type
        self.db_prefix = db_prefix
        self._database = database

    @property
    def database(self):
        return connections[self._database]

    @property
    def db_object(self):
        return Provider.objects.get(name=self.name)


class LocalAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, provider=None, **kwargs):
        if provider not in ('local', None):
            return None

        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            user = UserModel._default_manager.get(username=username, provider=None)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user


class XFAuthBackend:
    """
    Checks for a XenForo user, and if found, creates a settings.AUTH_USER_MODEL
    instance and authenticates against it.

    If a settings.AUTH_USER_MODEL instance already exists, the password will be
    set to the password hash from XenForo.

    Source: https://github.com/chrishas35/django-xenforo/blob/xf-auth/xenforo/backends.py
    """
    def get_auth_provider(self, provider):
        try:
            provider_config = settings.AUTH_PROVIDERS[provider]
        except KeyError:
            return None

        auth_provider = AuthProvider(name=provider, **provider_config)

        if auth_provider.type != 'xenforo':
            return None

        return auth_provider

    def authenticate(self, request, username=None, password=None, provider=None, **kwargs):
        if username is None:
            return None

        auth_provider = self.get_auth_provider(provider)

        if auth_provider is None:
            return None

        row = self.get_remote_user(username, auth_provider)
        if row is None:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            UserModel().set_password(password)
            return None

        user, created = UserModel.objects.get_or_create(**{
            UserModel.USERNAME_FIELD: username,
            'provider': auth_provider.db_object,
            'defaults': {
                'password': convert_to_django_password(row['scheme_class'],
                                                       row['data'])
            }
        })

        remote_group_ids = [group_id for group_id in row['secondary_group_ids'].decode().split(',')]
        remote_group_ids.append(row['user_group_id'])

        self.update_user_groups(user, auth_provider, remote_group_ids)

        if not created:
            user.password = convert_to_django_password(row['scheme_class'],
                                                       row['data'])
            user.save()

        if user.check_password(password):
            return user

    def get_remote_user(self, username, auth_provider):
        with auth_provider.database.cursor() as cursor:
            cursor.execute("""SELECT u.user_id, u.username,
                                    auth.scheme_class, auth.data,
                                    u.user_group_id, u.secondary_group_ids
                            FROM {prefix}user AS u,
                                {prefix}user_authenticate AS auth
                            WHERE u.username = %s
                                AND auth.user_id = u.user_id
                        """.format(prefix=auth_provider.db_prefix),
                        [username])
            try:
                return dictfetchall(cursor)[0]
            except IndexError:
                return None
        return None

    def update_user_groups(self, user, auth_provider, remote_group_ids):
        remote_provider_groups = Group.objects.filter(remotegroup__provider=auth_provider.db_object, remotegroup__remote_id__in=remote_group_ids)

        current = user.groups.all().exclude(remotegroup__provider=auth_provider.db_object)
        user.groups.set(current | remote_provider_groups)

