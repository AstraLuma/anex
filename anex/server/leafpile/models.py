from django.db import models
from django.conf import settings


class Node(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    source = models.TextField()
