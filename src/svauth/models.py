from django.db import models
from django.contrib.auth.models import AbstractUser, Group


class User(AbstractUser):
    xf_user_id = models.PositiveIntegerField(null=True, blank=True, unique=True)


class RemoteGroup(models.Model):
    remote_id = models.PositiveIntegerField()
    local_group = models.ForeignKey(Group, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('local_group', 'remote_id')

