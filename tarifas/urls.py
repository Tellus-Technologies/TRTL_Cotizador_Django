from rest_framework.routers import DefaultRouter
from .views import TarifaViewSet


router = DefaultRouter()

router.register(
    r'tarifas',
    TarifaViewSet,
    basename='tarifas'
)

urlpatterns = router.urls