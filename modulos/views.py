from django.db import connection
from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import Modulo
from .serializers import ModuloSerializer


class ModuloViewSet(viewsets.ModelViewSet):
    queryset = Modulo.objects.all().order_by('id')
    serializer_class = ModuloSerializer

    def destroy(self, request, *args, **kwargs):
        modulo = self.get_object()

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1
                FROM tarifas
                WHERE modulo_id = %s
                LIMIT 1
                """,
                [modulo.id]
            )

            tiene_tarifas = cursor.fetchone() is not None

        if tiene_tarifas:
            return Response(
                {
                    "error":
                    "No se puede eliminar el módulo porque tiene tarifas asociadas"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        modulo.delete()

        return Response(
            {"success": True},
            status=status.HTTP_200_OK
        )