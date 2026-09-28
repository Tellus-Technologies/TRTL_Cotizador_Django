from django.db import models


class Modulo(models.Model):
    modu = models.CharField(
        unique=True,
        max_length=100
    )

    descrip = models.CharField(
        max_length=300,
        blank=True,
        null=True
    )

    class Meta:
        managed = False
        db_table = 'modulos'

    def __str__(self):
        return self.modu