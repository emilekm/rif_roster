from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    xf_user_id = models.CharField(max_length=64, null=True, blank=True, unique=True)
