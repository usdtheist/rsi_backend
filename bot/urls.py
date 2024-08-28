from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, TradeViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet)
router.register(r'trades', TradeViewSet, basename='trade')

urlpatterns = [
  path('v1/', include(router.urls)),
]
