from rest_framework import viewsets

from .models import Tarifa
from .serializers import TarifaSerializer


class TarifaViewSet(viewsets.ModelViewSet):
    serializer_class = TarifaSerializer

    def get_queryset(self):
        queryset = (
            Tarifa.objects
            .select_related('cliente', 'modulo')
            .all()
            .order_by('id')
        )

        cliente_id = self.request.query_params.get('cliente_id')
        modulo_id = self.request.query_params.get('modulo_id')
        anio_fiscal = self.request.query_params.get('anio_fiscal')

        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)

        if modulo_id:
            queryset = queryset.filter(modulo_id=modulo_id)

        if anio_fiscal:
            queryset = queryset.filter(anio_fiscal=anio_fiscal)

        return queryset