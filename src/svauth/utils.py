'''
convert_to_django_password comes from https://github.com/chrishas35/django-xenforo/blob/xf-auth/xenforo/utils.py
'''
import phpserialize


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def convert_to_django_password(scheme_class, data):
    data = phpserialize.unserialize(data, decode_strings=True)

    if scheme_class == 'XenForo_Authentication_Core12':
        return 'xenforo_core12${hash}'.format(**data)
    elif scheme_class == 'XenForo_Authentication_Core':
        if data['hashFunc'] == 'sha256':
            return 'xenforo_sha256${salt}${hash}'.format(**data)
        if data['hashFunc'] == 'sha1':
            return 'xenforo_sha1${salt}${hash}'.format(**data)
    elif scheme_class == 'XenForo_Authentication_vBulletin':
        return 'vbulletin_md5${salt}${hash}'.format(**data)
