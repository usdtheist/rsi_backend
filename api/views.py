from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import UserStrategyFilter, StrategyFilter, CoinFilter
from .models import User, Strategy, UserStrategy, Coin
from bot.models import Order
from bot.binance.b_client import BinanceClient
from .serializers import CoinSerializer, StrategySerializer, UserSerializer, UserStrategySerializer, CustomTokenObtainPairSerializer, UserRegistrationSerializer, PasswordChangeSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserRegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.all().distinct() if user.is_staff else User.objects.filter(id=user.id)

        active = self.request.query_params.get('active', None)
        if active is not None:
            active_bool = active.lower() == 'true'
            queryset = queryset.filter(active=active_bool)

        return queryset.order_by('id')

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        if not user.is_staff:
            kwargs['pk'] = user.id
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='balance')
    def balance(self, request):
        user = request.user
        binance_client = BinanceClient(user.client_id, user.client_secret)
        balance = binance_client.fetch_account()
        return Response({"balance": balance}, status=status.HTTP_200_OK)

class CoinViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = Coin.objects.all().distinct()
    serializer_class = CoinSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CoinFilter

class StrategyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = Strategy.objects.all().order_by('id')
    serializer_class = StrategySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = StrategyFilter

    @action(detail=False, methods=['post'], url_path='bulk')
    def bulk_update(self, request):
        for str_data in request.data:
            strategy = Strategy.objects.get(id=str_data['id'])
            strategy.recommended = str_data['recommended']

            strategy.save()

        return Response({"message": "All strategies updated successfully."}, status=status.HTTP_200_OK)

class UserStrategyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = UserStrategy.objects.all()
    serializer_class = UserStrategySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserStrategyFilter

    @action(detail=True, methods=['get'], url_path='reset')
    def reset(self, request, pk=None):
        user_strategy = self.get_object()

        order = Order.objects.filter(user_strategy__id=user_strategy.id, order_type='BUY', parent__isnull=True)
        order.delete()

        user_strategy_serializer = UserStrategySerializer(user_strategy).data
        return Response(user_strategy_serializer)
