'''
Xenforo hashers come from https://github.com/chrishas35/django-xenforo/blob/xf-auth/xenforo/hashers.py
'''
from collections import OrderedDict
import hashlib

from django.contrib.auth.hashers import BasePasswordHasher, mask_hash
from django.utils.crypto import constant_time_compare
from django.utils.encoding import force_bytes, force_text
from django.utils.translation import ugettext_noop as _


class XenForoSHA256PasswordHasher(BasePasswordHasher):
    """
    The XenForo sha256 password hashing algorithm.
    """
    algorithm = 'xenforo_sha256'
    digest = hashlib.sha256
    salt_show = 6

    def encode(self, password, salt):
        assert password
        assert salt and '$' not in salt
        hash = self.digest(force_bytes('%s%s' % (self.digest(force_bytes(password)).hexdigest(), salt))).hexdigest()
        return '%s$%s$%s' % (self.algorithm, salt, hash)

    def verify(self, password, encoded):
        algorithm, salt, hash = encoded.split('$', 2)
        assert algorithm == self.algorithm
        encoded_2 = self.encode(password, salt)
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        algorithm, salt, hash = encoded.split('$', 2)
        assert algorithm == self.algorithm
        return OrderedDict([
            (_('algorithm'), algorithm),
            (_('salt'), mask_hash(salt, show=self.salt_show)),
            (_('hash'), mask_hash(hash)),
        ])


class XenForoSHA1PasswordHasher(XenForoSHA256PasswordHasher):
    """
    The XenForo sha1 password hashing algorithm.
    """
    algorithm = "xenforo_sha1"
    digest = hashlib.sha1


class VBulletinPasswordHasher(XenForoSHA256PasswordHasher):
    """
    The XenForo sha1 password hashing algorithm.
    """
    algorithm = "vbulletin_md5"
    digest = hashlib.md5
    salt_show = 0

class XenForoCore12PasswordHasher(BasePasswordHasher):
    """
    The XenForo Core 1.2 Password Hasher.

    Uses bcrypt, so basing on django.contrib.auth.hashers.BCryptPasswordHasher
    """
    algorithm = 'xenforo_core12'
    library = ('bcrypt', 'bcrypt')
    rounds = 10

    def salt(self):
        bcrypt = self._load_library()
        return bcrypt.gensalt(self.rounds)

    def encode(self, password, salt):
        bcrypt = self._load_library()
        password = force_bytes(password)
        data = bcrypt.hashpw(password, salt)
        return "%s$%s" % (self.algorithm, force_text(data))

    def verify(self, password, encoded):
        algorithm, data = encoded.split('$', 1)
        assert algorithm == self.algorithm
        bcrypt = self._load_library()

        password = force_bytes(password)
        data = force_bytes(data)

        hashpw = force_bytes(bcrypt.hashpw(password, data))

        return constant_time_compare(data, hashpw)

    def safe_summary(self, encoded):
        algorithm, empty, algostr, work_factor, data = encoded.split('$', 4)
        assert algorithm == self.algorithm
        salt, checksum = data[:22], data[22:]
        return OrderedDict([
            (_('algorithm'), algorithm),
            (_('work factor'), work_factor),
            (_('salt'), mask_hash(salt)),
            (_('checksum'), mask_hash(checksum)),
        ])
