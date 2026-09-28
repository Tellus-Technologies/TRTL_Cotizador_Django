from rest_framework import serializers
from .models import Cliente


class ClienteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cliente
        fields = [
            'id',
            'nombre',
            'comen',
        ]

    def validate_nombre(self, value):
        queryset = Cliente.objects.filter(nombre__iexact=value.strip())

        # Si estamos editando, excluir el registro actual
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un cliente con ese nombre"
            )

        return value.strip()