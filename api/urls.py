from django.urls import path, include
from .views import UserRegistrationView, SubscriptionViewSet
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CoinViewSet, StrategyViewSet, UserStrategyViewSet, CustomTokenObtainPairView, LogoutView, PasswordChangeView, ReferralViewSet, UserCoinViewSet, ContactUsViewSet, PasswordResetRequestView, PasswordResetConfirmView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'coins', CoinViewSet)
router.register(r'strategies', StrategyViewSet)
router.register(r'user_strategies', UserStrategyViewSet)
router.register(r'user_coins', UserCoinViewSet)
router.register(r'referrals', ReferralViewSet)
router.register(r'contact_us', ContactUsViewSet)
router.register(r'subscriptions', SubscriptionViewSet)

urlpatterns = [
  path('register/', UserRegistrationView.as_view(), name='register'),
  path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
  path('logout/', LogoutView.as_view(), name='logout'),
  path('change-password/', PasswordChangeView.as_view(), name='change-password'),
  path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
  path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
  path('v1/', include(router.urls)),
]
