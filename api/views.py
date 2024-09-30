from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import UserStrategyFilter
from .models import User, Strategy, UserStrategy, Coin
from .serializers import CoinSerializer, StrategySerializer, UserSerializer, UserStrategySerializer, CustomTokenObtainPairSerializer, UserRegistrationSerializer

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

        return queryset

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        if not user.is_staff:
            kwargs['pk'] = user.id
        return super().retrieve(request, *args, **kwargs)

class CoinViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = Coin.objects.all()
    serializer_class = CoinSerializer

class StrategyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer

class UserStrategyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = UserStrategy.objects.all().order_by('id')
    serializer_class = UserStrategySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserStrategyFilter

    def get_queryset(self):
        return UserStrategy.objects.filter(user_id=self.request.user.id).order_by('id')
