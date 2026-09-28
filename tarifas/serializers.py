from rest_framework import serializers

from clientes.models import Cliente
from modulos.models import Modulo
from .models import Tarifa


class TarifaSerializer(serializers.ModelSerializer):

    cliente_id = serializers.PrimaryKeyRelatedField(
        source='cliente',
        queryset=Cliente.objects.all()
    )

    modulo_id = serializers.PrimaryKeyRelatedField(
        source='modulo',
        queryset=Modulo.objects.all()
    )

    cliente_nombre = serializers.CharField(
        source='cliente.nombre',
        read_only=True
    )

    modulo_nombre = serializers.CharField(
        source='modulo.modu',
        read_only=True
    )

    class Meta:
        model = Tarifa
        fields = [
            'id',
            'cliente_id',
            'modulo_id',
            'anio_fiscal',
            'tarifa_mxn',
            'cliente_nombre',
            'modulo_nombre',
        ]

    def validate(self, data):
        cliente = data.get(
            'cliente',
            getattr(self.instance, 'cliente', None)
        )

        modulo = data.get(
            'modulo',
            getattr(self.instance, 'modulo', None)
        )

        anio_fiscal = data.get(
            'anio_fiscal',
            getattr(self.instance, 'anio_fiscal', None)
        )

        queryset = Tarifa.objects.filter(
            cliente=cliente,
            modulo=modulo,
            anio_fiscal=anio_fiscal
        )

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError({
                "error":
                "Ya existe una tarifa para este cliente, módulo y año"
            })

        return data