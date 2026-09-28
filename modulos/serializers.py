from rest_framework import serializers
from .models import Modulo


class ModuloSerializer(serializers.ModelSerializer):

    class Meta:
        model = Modulo
        fields = [
            'id',
            'modu',
            'descrip',
        ]

    def validate_modu(self, value):
        value = value.strip()

        queryset = Modulo.objects.filter(
            modu__iexact=value
        )

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un módulo con ese nombre"
            )

        return value