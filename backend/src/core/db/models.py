from django.db import models


class DBModel(models.Model):
    """Base abstract model using in app."""

    objects = models.Manager()

    class Meta:
        abstract = True
