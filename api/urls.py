from django.urls import path, include
from .views import UserRegistrationView
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CoinViewSet, StrategyViewSet, UserStrategyViewSet
from .views import CustomTokenObtainPairView, LogoutView, PasswordChangeView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'coins', CoinViewSet)
router.register(r'strategies', StrategyViewSet)
router.register(r'user_strategies', UserStrategyViewSet)

urlpatterns = [
  path('register/', UserRegistrationView.as_view(), name='register'),
  path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
  path('logout/', LogoutView.as_view(), name='logout'),
  path('change-password/', PasswordChangeView.as_view(), name='change-password'),
  path('v1/', include(router.urls)),
]
