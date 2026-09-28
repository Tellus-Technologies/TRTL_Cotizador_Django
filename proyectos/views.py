from decimal import Decimal, InvalidOperation

from django.db import connection, transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from clientes.models import Cliente
from modulos.models import Modulo

from .models import (
    Proyecto,
    ProyectoModulo,
    ProyectoFase,
    ProyectoFaseFecha,
    ProyectoRecurso,
    ProyectoRecursoFecha,
)

from .serializers import (
    ProyectoResumenSerializer,
    ProyectoModuloSerializer,
    ProyectoFaseSerializer,
    ProyectoRecursoSerializer,
)


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def to_decimal(value, default="0"):
    try:
        if value is None or value == "":
            return Decimal(default)

        return Decimal(str(value))

    except (InvalidOperation, ValueError, TypeError):
        return Decimal(default)


def to_int(value, default=0):
    try:
        if value is None or value == "":
            return default

        return int(value)

    except (ValueError, TypeError):
        return default


def normalizar_anios_fiscales(anios):
    if isinstance(anios, list):
        return ", ".join(str(anio) for anio in anios)

    return anios or None


def normalizar_fechas(fechas):
    if not isinstance(fechas, list):
        return []

    return sorted(
        {
            str(fecha)[:10]
            for fecha in fechas
            if fecha
        }
    )


# ============================================================
# LISTADO + CREACIÓN
# ============================================================

class ProyectoListView(APIView):

    # --------------------------------------------------------
    # GET /api/proyectos/
    # --------------------------------------------------------

    def get(self, request):

        proyectos = (
            Proyecto.objects
            .select_related('cliente')
            .all()
            .order_by('-created_at', '-id')
        )

        serializer = ProyectoResumenSerializer(
            proyectos,
            many=True
        )

        return Response(serializer.data)

    # --------------------------------------------------------
    # POST /api/proyectos/
    # --------------------------------------------------------

    def post(self, request):

        data = request.data

        cliente_id = data.get('cliente_id')
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')

        modulos = data.get('modulos', [])
        fases = data.get('fases', [])
        recursos = data.get('recursos', [])

        # ====================================================
        # VALIDACIONES
        # ====================================================

        if not cliente_id:
            return Response(
                {
                    "error": "El cliente es obligatorio"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not fecha_inicio or not fecha_fin:
            return Response(
                {
                    "error":
                    "Las fechas de inicio y fin son obligatorias"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if fecha_inicio > fecha_fin:
            return Response(
                {
                    "error":
                    "La fecha de inicio no puede ser mayor a la fecha final"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(modulos, list) or len(modulos) == 0:
            return Response(
                {
                    "error":
                    "Debes enviar al menos un módulo en el proyecto"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(fases, list) or len(fases) == 0:
            return Response(
                {
                    "error":
                    "Debes enviar las fases del proyecto"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(recursos, list) or len(recursos) == 0:
            return Response(
                {
                    "error":
                    "Debes enviar los recursos del proyecto"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Comprobar cliente
        if not Cliente.objects.filter(pk=cliente_id).exists():
            return Response(
                {
                    "error":
                    "El cliente seleccionado no existe"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Comprobar módulos
        ids_modulos = set()

        for item in modulos:
            if item.get('modulo_id'):
                ids_modulos.add(item.get('modulo_id'))

        for recurso in recursos:
            modulo_id = (
                recurso.get('modulo_id')
                or recurso.get('recurso_id')
            )

            if modulo_id:
                ids_modulos.add(modulo_id)

        modulos_existentes = set(
            Modulo.objects
            .filter(id__in=ids_modulos)
            .values_list('id', flat=True)
        )

        if ids_modulos != modulos_existentes:
            return Response(
                {
                    "error":
                    "Uno o más módulos enviados no existen"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validación de porcentaje de fases
        porcentaje_total = sum(
            to_decimal(fase.get('porcentaje'))
            for fase in fases
        )

        if porcentaje_total != Decimal("100"):
            return Response(
                {
                    "error":
                    "El porcentaje total de las fases debe sumar 100"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ====================================================
        # TOTALES
        # ====================================================

        subtotal_mxn = to_decimal(
            data.get('subtotal_mxn', data.get('total_mxn'))
        )

        subtotal_usd = to_decimal(
            data.get('subtotal_usd', data.get('total_usd'))
        )

        descuento_mxn = to_decimal(
            data.get('descuento_mxn')
        )

        descuento_usd = to_decimal(
            data.get('descuento_usd')
        )

        total_final_mxn = to_decimal(
            data.get(
                'total_final_mxn',
                data.get('total_mxn', subtotal_mxn)
            )
        )

        total_final_usd = to_decimal(
            data.get(
                'total_final_usd',
                data.get('total_usd', subtotal_usd)
            )
        )

        # ====================================================
        # TRANSACCIÓN
        # ====================================================

        try:

            with transaction.atomic():

                # ------------------------------------------------
                # 1. CREAR CABECERA DEL PROYECTO
                # ------------------------------------------------
                #
                # Se usa SQL aquí porque numero_proyecto
                # tiene un DEFAULT/SEQUENCE en PostgreSQL.
                #
                # NO lo enviamos para que PostgreSQL lo genere.
                # ------------------------------------------------

                with connection.cursor() as cursor:

                    cursor.execute(
                        """
                        INSERT INTO proyectos (
                            cliente_id,
                            nombre_proyecto,
                            metodologia,
                            fecha_inicio,
                            fecha_fin,
                            tipo_cambio,
                            anios_fiscales,

                            subtotal_mxn,
                            subtotal_usd,

                            tipo_descuento,
                            valor_descuento,
                            descuento_mxn,
                            descuento_usd,

                            total_final_mxn,
                            total_final_usd,

                            comentario_proyecto,

                            total_mxn,
                            total_usd,
                            total_dias,
                            total_horas
                        )
                        VALUES (
                            %s, %s, %s, %s, %s, %s, %s,
                            %s, %s,
                            %s, %s, %s, %s,
                            %s, %s,
                            %s,
                            %s, %s, %s, %s
                        )
                        RETURNING id, numero_proyecto
                        """,
                        [
                            cliente_id,
                            data.get('nombre_proyecto') or None,
                            data.get('metodologia') or None,
                            fecha_inicio,
                            fecha_fin,
                            to_decimal(data.get('tipo_cambio')),
                            normalizar_anios_fiscales(
                                data.get('anios_fiscales')
                            ),

                            subtotal_mxn,
                            subtotal_usd,

                            data.get('tipo_descuento') or None,
                            to_decimal(
                                data.get('valor_descuento')
                            ),
                            descuento_mxn,
                            descuento_usd,

                            total_final_mxn,
                            total_final_usd,

                            data.get('comentario_proyecto') or None,

                            total_final_mxn,
                            total_final_usd,

                            to_int(data.get('total_dias')),
                            to_int(data.get('total_horas')),
                        ]
                    )

                    proyecto_id, numero_proyecto = cursor.fetchone()

                # ------------------------------------------------
                # 2. MÓDULOS DEL PROYECTO
                # ------------------------------------------------

                for item in modulos:

                    ProyectoModulo.objects.create(
                        proyecto_id=proyecto_id,
                        modulo_id=item.get('modulo_id'),

                        tarifa_mxn=to_decimal(
                            item.get('tarifa_mxn')
                        ),

                        dias=to_int(
                            item.get('dias')
                        ),

                        horas=to_int(
                            item.get('horas')
                        ),

                        total_mxn=to_decimal(
                            item.get('total_mxn')
                        ),

                        total_usd=to_decimal(
                            item.get('total_usd')
                        ),
                    )

                # ------------------------------------------------
                # 3. FASES + FECHAS
                # ------------------------------------------------

                for index, fase in enumerate(fases):

                    monto_estimado_mxn = to_decimal(
                        fase.get(
                            'monto_estimado_mxn',
                            fase.get('monto_mxn')
                        )
                    )

                    monto_estimado_usd = to_decimal(
                        fase.get(
                            'monto_estimado_usd',
                            fase.get('monto_usd')
                        )
                    )

                    monto_final_mxn = to_decimal(
                        fase.get(
                            'monto_final_mxn',
                            fase.get(
                                'monto_mxn',
                                monto_estimado_mxn
                            )
                        )
                    )

                    monto_final_usd = to_decimal(
                        fase.get(
                            'monto_final_usd',
                            fase.get(
                                'monto_usd',
                                monto_estimado_usd
                            )
                        )
                    )

                    proyecto_fase = ProyectoFase.objects.create(
                        proyecto_id=proyecto_id,

                        orden_fase=(
                            fase.get('orden_fase')
                            or index + 1
                        ),

                        nombre_fase=(
                            fase.get('nombre_fase')
                            or fase.get('nombre')
                            or f"Fase {index + 1}"
                        ),

                        dias=to_int(
                            fase.get('dias')
                        ),

                        porcentaje=to_decimal(
                            fase.get('porcentaje')
                        ),

                        plan_inicio=(
                            fase.get('plan_inicio')
                            if fase.get('plan_inicio') not in [None, ""]
                            else None
                        ),

                        monto_mxn=monto_final_mxn,
                        monto_usd=monto_final_usd,

                        monto_estimado_mxn=monto_estimado_mxn,
                        monto_estimado_usd=monto_estimado_usd,

                        monto_final_mxn=monto_final_mxn,
                        monto_final_usd=monto_final_usd,
                    )

                    fechas = normalizar_fechas(
                        fase.get('fechas_asignadas')
                    )

                    for fecha in fechas:

                        ProyectoFaseFecha.objects.create(
                            proyecto_fase=proyecto_fase,
                            fecha=fecha
                        )

                # ------------------------------------------------
                # 4. RECURSOS + FECHAS
                # ------------------------------------------------

                for index, recurso in enumerate(recursos):

                    modulo_id = (
                        recurso.get('modulo_id')
                        or recurso.get('recurso_id')
                    )

                    proyecto_recurso = (
                        ProyectoRecurso.objects.create(
                            proyecto_id=proyecto_id,

                            modulo_id=modulo_id,

                            recurso_numero=(
                                recurso.get('recurso_numero')
                                or index + 1
                            ),

                            tarifa_hora=to_decimal(
                                recurso.get('tarifa_hora')
                            ),

                            dias_asignados=to_int(
                                recurso.get('dias_asignados')
                            ),

                            horas=to_int(
                                recurso.get('horas')
                            ),

                            total_mxn=to_decimal(
                                recurso.get('total_mxn')
                            ),

                            total_usd=to_decimal(
                                recurso.get('total_usd')
                            ),
                        )
                    )

                    fechas = normalizar_fechas(
                        recurso.get('fechas_asignadas')
                    )

                    for fecha in fechas:

                        ProyectoRecursoFecha.objects.create(
                            proyecto_recurso=proyecto_recurso,
                            fecha=fecha
                        )

                # ------------------------------------------------
                # 5. LEER PROYECTO CREADO
                # ------------------------------------------------

                proyecto = (
                    Proyecto.objects
                    .select_related('cliente')
                    .get(pk=proyecto_id)
                )

                serializer = ProyectoResumenSerializer(
                    proyecto
                )

                return Response(
                    {
                        "success": True,
                        "id": proyecto_id,
                        "numero_proyecto": numero_proyecto,
                        "proyecto": serializer.data,
                        "message":
                            f"Proyecto {numero_proyecto} creado con éxito"
                    },
                    status=status.HTTP_201_CREATED
                )

        except Exception as error:

            print(
                "ERROR AL CREAR PROYECTO:",
                repr(error)
            )

            return Response(
                {
                    "error":
                    "Ocurrió un error al crear el proyecto",
                    "detalle": str(error)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================
# DETALLE
# ============================================================

class ProyectoDetalleView(APIView):

    def get(self, request, pk):

        try:

            proyecto = (
                Proyecto.objects
                .select_related('cliente')
                .get(pk=pk)
            )

        except Proyecto.DoesNotExist:

            return Response(
                {
                    "error":
                    "Proyecto no encontrado"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        proyecto_data = ProyectoResumenSerializer(
            proyecto
        ).data

        proyecto_data["cliente_comentario"] = (
            proyecto.cliente.comen
        )

        modulos = (
            proyecto.modulos_proyecto
            .select_related('modulo')
            .all()
            .order_by('id')
        )

        fases = (
            proyecto.fases
            .prefetch_related('fechas')
            .all()
            .order_by('orden_fase', 'id')
        )

        recursos = (
            proyecto.recursos
            .select_related('modulo')
            .prefetch_related('fechas')
            .all()
            .order_by(
                'modulo_id',
                'recurso_numero',
                'id'
            )
        )

        return Response({
            "proyecto":
                proyecto_data,

            "modulos":
                ProyectoModuloSerializer(
                    modulos,
                    many=True
                ).data,

            "fases":
                ProyectoFaseSerializer(
                    fases,
                    many=True
                ).data,

            "recursos":
                ProyectoRecursoSerializer(
                    recursos,
                    many=True
                ).data,
        })