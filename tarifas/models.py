from django.db import models

# Create your models here.
from django.db import models

from clientes.models import Cliente
from modulos.models import Modulo


class Tarifa(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        db_column='cliente_id',
        blank=True,
        null=True,
    )

    modulo = models.ForeignKey(
        Modulo,
        on_delete=models.CASCADE,
        db_column='modulo_id',
        blank=True,
        null=True,
    )

    anio_fiscal = models.CharField(
        max_length=10
    )

    tarifa_mxn = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        managed = False
        db_table = 'tarifas'
        constraints = [
            models.UniqueConstraint(
                fields=['cliente', 'modulo', 'anio_fiscal'],
                name='unique_cliente_modulo_anio'
            )
        ]

    def __str__(self):
        return f"{self.cliente} - {self.modulo} - {self.anio_fiscal}"