from django.db import connections
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Group
from django.conf import settings

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
