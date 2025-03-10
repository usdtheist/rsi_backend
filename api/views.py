from rest_framework import viewsets, status
from django.template.loader import render_to_string
from rest_framework.decorators import action
from django.contrib.auth.tokens import default_token_generator
from rsi_project.mail.backend.smtp import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils.encoding import force_bytes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import UserStrategyFilter, StrategyFilter, CoinFilter, ReferralsFilter, UserCoinFilter, ContactUsFilter
from .models import User, Strategy, UserStrategy, Coin, Referrals, UserCoin, ContactUs
from django.db.models import Sum, DecimalField, F
from django.db.models.functions import Coalesce
from bot.models import Order
from bot.binance.b_client import BinanceClient
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from .serializers import CoinSerializer, StrategySerializer, UserSerializer, UserStrategySerializer, CustomTokenObtainPairSerializer, UserRegistrationSerializer, PasswordChangeSerializer, ReferralsSerializer, UserCoinSerializer, ContactUsSerializer
import os

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserRegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(APIView):
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()

        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"{os.environ.get('NEXT_APP_URL')}/reset-password/{uid}/{token}/"

            html_content = render_to_string('emails/password_reset_email.html', {'reset_url': reset_url, 'user': user})
            send_mail("Password Reset Request", user.email, html_content)

            return Response({"message": "Password reset link has been sent to your email."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "No account found with this email."}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(APIView):
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid link"}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        new_password = request.data.get('password')
        user.set_password(new_password)
        user.save()

        return Response({"message": "Password has been reset successfully"}, status=status.HTTP_200_OK)

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

class UserCoinViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserCoinSerializer
    queryset = UserCoin.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserCoinFilter

class ReferralViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = Referrals.objects.all().distinct()
    serializer_class = ReferralsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReferralsFilter

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request, *args, **kwargs):
        user = request.user
        queryset = self.get_queryset().filter(referrer=user)

        return Response({
            'count': queryset.count(),
            'pending_amount': queryset.filter(payment_status='pending').aggregate(Sum(F('payment_amount')))['payment_amount__sum'],
            'paid_amount': queryset.filter(payment_status='paid').aggregate(Sum(F('payment_amount')))['payment_amount__sum']
        })

class ContactUsViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = ContactUs.objects.all().order_by('-created_at')
    serializer_class = ContactUsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ContactUsFilter
