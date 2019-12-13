from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _


class Provider(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    # Redefining 'username' field to remove orig. 'unique' attr
    username = models.CharField(
        _('username'),
        max_length=150,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[UnicodeUsernameValidator()],
    )

    is_machine = models.BooleanField(default=False)

    provider = models.ForeignKey(Provider, null=True, on_delete=models.PROTECT)

    class Meta:
        unique_together = ('username', 'provider')


class RemoteGroup(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    remote_id = models.TextField()
    local_group = models.ForeignKey(Group, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('provider', 'remote_id')
