from django.db import connection
from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import Cliente
from .serializers import ClienteSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all().order_by('id')
    serializer_class = ClienteSerializer

    def destroy(self, request, *args, **kwargs):
        cliente = self.get_object()

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1
                FROM tarifas
                WHERE cliente_id = %s
                LIMIT 1
                """,
                [cliente.id]
            )

            tiene_tarifas = cursor.fetchone() is not None

        if tiene_tarifas:
            return Response(
                {
                    "error":
                    "No se puede eliminar el cliente porque tiene tarifas asociadas"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        cliente.delete()

        return Response(
            {"success": True},
            status=status.HTTP_200_OK
        )