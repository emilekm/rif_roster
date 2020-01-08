from django.db import connections
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Group
from django.conf import settings

from svauth.models import RemoteGroup
from svauth.utils import dictfetchall, convert_to_django_password

UserModel = get_user_model()



class LocalAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            user = UserModel._default_manager.get(username=username)
            if user.xf_user_id:
                return None
            return user
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user


class XFAuthBackend(ModelBackend):
    """
    Checks for a XenForo user, and if found, creates a settings.AUTH_USER_MODEL
    instance and authenticates against it.

    If a settings.AUTH_USER_MODEL instance already exists, the password will be
    set to the password hash from XenForo.

    Source: https://github.com/chrishas35/django-xenforo/blob/xf-auth/xenforo/backends.py
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            return None

        row = self.get_remote_user(username)
        if row is None:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            UserModel().set_password(password)
            return None

        try:
            user = UserModel.objects.get(xf_user_id=row['user_id'])
            created = False
        except UserModel.DoesNotExist:
            user, created = UserModel.objects.get_or_create(**{
                UserModel.USERNAME_FIELD: username,
                'defaults': {
                    'xf_user_id': row['user_id'],
                    'password': convert_to_django_password(row['scheme_class'],
                                                           row['data'])
                }
            })

        if not created:
            user.password = convert_to_django_password(row['scheme_class'],
                                                       row['data'])
            user.xf_user_id = row['user_id']
            setattr(user, UserModel.USERNAME_FIELD, row['username'])
            user.save()

        self.update_user_groups(user)

        if user.check_password(password):
            return user

    def get_remote_user(self, username):
        with connections['xenforo'].cursor() as cursor:
            cursor.execute("""SELECT u.user_id, u.username,
                                    auth.scheme_class, auth.data
                            FROM xf_user AS u,
                                xf_user_authenticate AS auth
                            WHERE u.username = %s
                                AND auth.user_id = u.user_id
                        """, [username])
            try:
                return dictfetchall(cursor)[0]
            except IndexError:
                return None
        return None

    def update_user_groups(self, user):
        with connections['xenforo'].cursor() as cursor:
            cursor.execute("""SELECT user_group_id
                            FROM xf_user_group_relation
                            WHERE user_id = %s
                        """, [user.xf_user_id])
            remote_group_ids = [row['user_group_id'] for row in dictfetchall(cursor)]
            print(remote_group_ids)

        groups_with_remote = Group.objects.filter(remotegroup__isnull=False)

        local_groups = user.groups.exclude(pk__in=groups_with_remote.values_list('pk', flat=True))

        user.groups.set(local_groups | groups_with_remote.filter(remotegroup__remote_id__in=remote_group_ids))
