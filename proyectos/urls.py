from django.urls import path

from .views import (
    ProyectoListView,
    ProyectoDetalleView,
)


urlpatterns = [
    path(
        'proyectos/',
        ProyectoListView.as_view(),
        name='proyectos-list'
    ),

    path(
        'proyectos/<int:pk>/',
        ProyectoDetalleView.as_view(),
        name='proyectos-detalle'
    ),
]