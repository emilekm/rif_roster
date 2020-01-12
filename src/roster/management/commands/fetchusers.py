from itertools import islice

from django.db import connections
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from svauth.models import RemoteGroup
from svauth.utils import dictfetchall

User = get_user_model()

remote_ids = RemoteGroup.objects.all().values_list('remote_id', flat=True).distinct()

query = ["SELECT xf_user.user_id as xf_user_id, xf_user.username as username FROM xf_user"]

if remote_ids:
    query.append("JOIN xf_user_group_relation ON xf_user_group_relation.user_id=xf_user.user_id WHERE")
    for group_id in remote_ids:
        query.append("xf_user_group_relation.user_group_id={}".format(group_id))
        query.append("OR")

    query.pop()

query = " ".join(query)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with connections['xenforo'].cursor() as cursor:
            # load users in either the GSI or PRF team groups
            cursor.execute(query)
            rows = dictfetchall(cursor)
            objs = [User(username=row['username'], xf_user_id=row['xf_user_id']) for row in rows]
            existing_users = User.objects.in_bulk([row['xf_user_id'] for row in rows], field_name='xf_user_id')

            batch_size = 100
            #Create new users
            User.objects.bulk_create(objs, batch_size, ignore_conflicts=True)
            # Update username on old objects
            User.objects.bulk_update(existing_users.values(), ['username'], batch_size)

            print('Fetched {} users information'.format(len(objs)))
