from django.db import models


class Cliente(models.Model):
    nombre = models.CharField(
        unique=True,
        max_length=100
    )

    comen = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    class Meta:
        managed = False
        db_table = 'clientes'

    def __str__(self):
        return self.nombre

        