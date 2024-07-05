from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CoinViewSet, StrategyViewSet, UserStrategyViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'coins', CoinViewSet)
router.register(r'strategies', StrategyViewSet)
router.register(r'user_strategies', UserStrategyViewSet)

urlpatterns = [
  path('v1/', include(router.urls)),
]
