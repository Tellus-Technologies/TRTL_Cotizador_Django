from rest_framework import serializers

from .models import (
    Proyecto,
    ProyectoModulo,
    ProyectoFase,
    ProyectoRecurso,
)


class ProyectoResumenSerializer(serializers.ModelSerializer):
    cliente_id = serializers.IntegerField(
        source='cliente.id',
        read_only=True
    )

    cliente_nombre = serializers.CharField(
        source='cliente.nombre',
        read_only=True
    )

    class Meta:
        model = Proyecto

        fields = [
            'id',
            'numero_proyecto',
            'cliente_id',
            'cliente_nombre',
            'nombre_proyecto',
            'metodologia',
            'fecha_inicio',
            'fecha_fin',
            'tipo_cambio',
            'anios_fiscales',

            'subtotal_mxn',
            'subtotal_usd',

            'tipo_descuento',
            'valor_descuento',
            'descuento_mxn',
            'descuento_usd',

            'total_final_mxn',
            'total_final_usd',

            'comentario_proyecto',

            'total_mxn',
            'total_usd',
            'total_dias',
            'total_horas',

            'created_at',
            'updated_at',
        ]


class ProyectoModuloSerializer(serializers.ModelSerializer):
    modulo_id = serializers.IntegerField(
        source='modulo.id',
        read_only=True
    )

    modulo_nombre = serializers.CharField(
        source='modulo.modu',
        read_only=True
    )

    modulo_descripcion = serializers.CharField(
        source='modulo.descrip',
        read_only=True
    )

    class Meta:
        model = ProyectoModulo

        fields = [
            'id',
            'proyecto_id',
            'modulo_id',
            'modulo_nombre',
            'modulo_descripcion',
            'tarifa_mxn',
            'dias',
            'horas',
            'total_mxn',
            'total_usd',
        ]


class ProyectoFaseSerializer(serializers.ModelSerializer):
    fechas_asignadas = serializers.SerializerMethodField()

    class Meta:
        model = ProyectoFase

        fields = [
            'id',
            'proyecto_id',
            'orden_fase',
            'nombre_fase',
            'dias',
            'porcentaje',
            'plan_inicio',

            'monto_mxn',
            'monto_usd',

            'monto_estimado_mxn',
            'monto_estimado_usd',

            'monto_final_mxn',
            'monto_final_usd',

            'fechas_asignadas',
        ]

    def get_fechas_asignadas(self, obj):
        return [
            item.fecha
            for item in obj.fechas.all().order_by('fecha')
        ]


class ProyectoRecursoSerializer(serializers.ModelSerializer):
    modulo_id = serializers.IntegerField(
        source='modulo.id',
        read_only=True
    )

    modulo_nombre = serializers.CharField(
        source='modulo.modu',
        read_only=True
    )

    modulo_descripcion = serializers.CharField(
        source='modulo.descrip',
        read_only=True
    )

    fechas_asignadas = serializers.SerializerMethodField()

    class Meta:
        model = ProyectoRecurso

        fields = [
            'id',
            'proyecto_id',
            'modulo_id',
            'modulo_nombre',
            'modulo_descripcion',

            'recurso_numero',
            'tarifa_hora',
            'dias_asignados',
            'horas',
            'total_mxn',
            'total_usd',

            'fechas_asignadas',
        ]

    def get_fechas_asignadas(self, obj):
        return [
            item.fecha
            for item in obj.fechas.all().order_by('fecha')
        ]