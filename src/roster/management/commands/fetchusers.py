from itertools import islice

from django.db import connections
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from svauth.utils import dictfetchall

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with connections['xenforo'].cursor() as cursor:
            cursor.execute("""SELECT user_id as xf_user_id, username
                            FROM xf_user""")
            rows = dictfetchall(cursor)
            objs = [User(username=row['username'], xf_user_id=row['xf_user_id']) for row in rows]
            existing_users = User.objects.in_bulk([row['xf_user_id'] for row in rows], field_name='xf_user_id')

            batch_size = 100
            #Create new users
            User.objects.bulk_create(objs, batch_size, ignore_conflicts=True)
            # Update username on old objects
            User.objects.bulk_update(existing_users.values(), ['username'], batch_size)

            print('Fetched {} users information'.format(len(objs)))
