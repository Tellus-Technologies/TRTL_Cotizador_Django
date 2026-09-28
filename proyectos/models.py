from django.db import models

from clientes.models import Cliente
from modulos.models import Modulo


class Proyecto(models.Model):
    numero_proyecto = models.BigIntegerField(
        unique=True,
        editable=False
    )

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.DO_NOTHING,
        db_column='cliente_id',
        related_name='proyectos'
    )

    nombre_proyecto = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    metodologia = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    fecha_inicio = models.DateField(
        blank=True,
        null=True
    )

    fecha_fin = models.DateField(
        blank=True,
        null=True
    )

    tipo_cambio = models.DecimalField(
        max_digits=14,
        decimal_places=4
    )

    anios_fiscales = models.TextField(
        blank=True,
        null=True
    )

    total_mxn = models.DecimalField(
        max_digits=16,
        decimal_places=2
    )

    total_usd = models.DecimalField(
        max_digits=16,
        decimal_places=2
    )

    total_dias = models.IntegerField()

    total_horas = models.IntegerField()

    created_at = models.DateTimeField()

    updated_at = models.DateTimeField()

    subtotal_mxn = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        blank=True,
        null=True
    )

    subtotal_usd = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        blank=True,
        null=True
    )

    tipo_descuento = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    valor_descuento = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        blank=True,
        null=True
    )

    descuento_mxn = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        blank=True,
        null=True
    )

    descuento_usd = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        blank=True,
        null=True
    )

    total_final_mxn = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        blank=True,
        null=True
    )

    total_final_usd = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        blank=True,
        null=True
    )

    comentario_proyecto = models.TextField(
        blank=True,
        null=True
    )

    class Meta:
        managed = False
        db_table = 'proyectos'

    def __str__(self):
        return f"{self.numero_proyecto} - {self.nombre_proyecto or 'Proyecto'}"


class ProyectoModulo(models.Model):
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        db_column='proyecto_id',
        related_name='modulos_proyecto'
    )

    modulo = models.ForeignKey(
        Modulo,
        on_delete=models.DO_NOTHING,
        db_column='modulo_id'
    )

    tarifa_mxn = models.DecimalField(
        max_digits=16,
        decimal_places=2
    )

    dias = models.IntegerField()

    horas = models.IntegerField()

    total_mxn = models.DecimalField(
        max_digits=16,
        decimal_places=2
    )

    total_usd = models.DecimalField(
        max_digits=16,
        decimal_places=2
    )

    class Meta:
        managed = False
        db_table = 'proyecto_modulos'


class ProyectoFase(models.Model):
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        db_column='proyecto_id',
        related_name='fases'
    )

    orden_fase = models.IntegerField()

    nombre_fase = models.CharField(max_length=255)

    dias = models.IntegerField()

    porcentaje = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    plan_inicio = models.IntegerField(
        blank=True,
        null=True
    )

    monto_mxn = models.DecimalField(
        max_digits=16,
        decimal_places=2
    )

    monto_usd = models.DecimalField(
        max_digits=16,
        decimal_places=2
    )

    monto_estimado_mxn = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        blank=True,
        null=True
    )

    monto_estimado_usd = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        blank=True,
        null=True
    )

    monto_final_mxn = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        blank=True,
        null=True
    )

    monto_final_usd = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        blank=True,
        null=True
    )

    class Meta:
        managed = False
        db_table = 'proyecto_fases'


class ProyectoFaseFecha(models.Model):
    proyecto_fase = models.ForeignKey(
        ProyectoFase,
        on_delete=models.CASCADE,
        db_column='proyecto_fase_id',
        related_name='fechas'
    )

    fecha = models.DateField()

    class Meta:
        managed = False
        db_table = 'proyecto_fase_fechas'


class ProyectoRecurso(models.Model):
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        db_column='proyecto_id',
        related_name='recursos'
    )

    modulo = models.ForeignKey(
        Modulo,
        on_delete=models.DO_NOTHING,
        db_column='modulo_id'
    )

    tarifa_hora = models.DecimalField(
        max_digits=16,
        decimal_places=2
    )

    dias_asignados = models.IntegerField()

    horas = models.IntegerField()

    total_mxn = models.DecimalField(
        max_digits=16,
        decimal_places=2
    )

    total_usd = models.DecimalField(
        max_digits=16,
        decimal_places=2
    )

    recurso_numero = models.IntegerField(
        blank=True,
        null=True
    )

    class Meta:
        managed = False
        db_table = 'proyecto_recursos'


class ProyectoRecursoFecha(models.Model):
    proyecto_recurso = models.ForeignKey(
        ProyectoRecurso,
        on_delete=models.CASCADE,
        db_column='proyecto_recurso_id',
        related_name='fechas'
    )

    fecha = models.DateField()

    class Meta:
        managed = False
        db_table = 'proyecto_recurso_fechas'