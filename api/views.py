from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import UserStrategyFilter
from .models import User, Strategy, UserStrategy, Coin
from .serializers import CoinSerializer, StrategySerializer, UserSerializer, CoinSerializer, UserStrategySerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CoinViewSet(viewsets.ModelViewSet):
    queryset = Coin.objects.all()
    serializer_class = CoinSerializer

class StrategyViewSet(viewsets.ModelViewSet):
    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer

class UserStrategyViewSet(viewsets.ModelViewSet):
    queryset = UserStrategy.objects.all().order_by('id')
    serializer_class = UserStrategySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserStrategyFilter
