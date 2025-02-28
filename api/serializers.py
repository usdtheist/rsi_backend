from rest_framework import serializers
from .models import User, Coin, Strategy, UserStrategy, Referrals, UserCoin, ContactUs
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from bot.binance.b_client import BinanceClient

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True, required=True)

  class Meta:
    model = User
    fields = ['email', 'full_name', 'password', 'referral_code', 'phone_number']

  def validate_password(self, value):
    if len(value) < 5:
      raise serializers.ValidationError("Password must be at least 6 characters long.")
    return value

  def create(self, validated_data):
    user = User.objects.create(
      email=validated_data['email'],
      full_name=validated_data['full_name']
    )
    user.set_password(validated_data['password'])
    user.save()

    if validated_data['referral_code']:
      try:
        referrer = User.objects.get(referral_code=validated_data['referral_code'])
        Referrals.objects.create(
          code=validated_data['referral_code'],
          referred_user=user,
          referrer=referrer,
        )

      except User.DoesNotExist:
        pass

    return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
  def validate(self, attrs):
    email = attrs.get('email')
    password = attrs.get('password')

    user = authenticate(email=email, password=password)
    if user:
      resp = super().validate(attrs)
      response = {
        'access': resp['access'],
        'refresh': resp['refresh'],
        'user': UserSerializer(user).data,
      }

      return response

    raise serializers.ValidationError('Invalid credentials')

class UserSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(read_only=True)
  role = serializers.SerializerMethodField()

  class Meta:
    model = User
    fields = ['id', 'full_name', 'email', 'phone_number', 'whatsapp_number', 'active', 'active',
              'client_id', 'client_secret', 'is_staff', 'payment_receipt_url', 'approved_at',
              'role', 'date_joined', 'auto_recommended', 'referral_code', 'profile_image_url',
              'wallet_address',
              ]

  def get_role(self, obj):
      return 'Admin' if obj.is_staff else 'User'

  def update(self, instance, validated_data):
    instance.client_id = validated_data.get('client_id', instance.client_id)
    instance.client_secret = validated_data.get('client_secret', instance.client_secret)

    try:
      existing_user = User.objects.get(id=instance.id)

      if instance.client_id != existing_user.client_id or instance.client_secret != existing_user.client_secret:
        binance_client = BinanceClient(instance.client_id, instance.client_secret)
        binance_client.fetch_account()
    except Exception:
      raise serializers.ValidationError("Invalid secrets provided")

    instance.is_staff = validated_data.get('is_staff', instance.is_staff)
    instance.full_name = validated_data.get('full_name', instance.full_name)
    instance.active = validated_data.get('active', instance.active)
    instance.payment_receipt_url = validated_data.get('payment_receipt_url', instance.payment_receipt_url)
    instance.approved_at = validated_data.get('approved_at', instance.approved_at)
    instance.auto_recommended = validated_data.get('auto_recommended', instance.auto_recommended)
    instance.referral_code = validated_data.get('referral_code', instance.referral_code)
    instance.profile_image_url = validated_data.get('profile_image_url', instance.profile_image_url)
    instance.phone_number = validated_data.get('phone_number', instance.phone_number)
    instance.whatsapp_number = validated_data.get('whatsapp_number', instance.whatsapp_number)
    instance.wallet_address = validated_data.get('wallet_address', instance.wallet_address)

    instance.save()

    return instance

class PasswordChangeSerializer(serializers.Serializer):
  old_password = serializers.CharField(required=True)
  new_password = serializers.CharField(required=True)

  def validate_old_password(self, value):
    user = self.context['request'].user
    if not user.check_password(value):
      raise serializers.ValidationError("Old password is incorrect.")
    return value

  def validate_new_password(self, value):
    if len(value) < 5:
      raise serializers.ValidationError("Password must be at least 6 characters long.")
    return value

class CoinSerializer(serializers.ModelSerializer):
  class Meta:
    model = Coin
    fields = '__all__'

class StrategySerializer(serializers.ModelSerializer):
  class Meta:
    model = Strategy
    fields = '__all__'

class UserStrategySerializer(serializers.ModelSerializer):
  strategy_name = serializers.CharField(source='strategy_id.name', read_only=True)
  rsi_type = serializers.CharField(source='strategy_id.rsi_type', read_only=True)
  rsi_time = serializers.CharField(source='strategy_id.rsi_time', read_only=True)
  buy_at = serializers.CharField(source='strategy_id.buy_at', read_only=True)
  recommended = serializers.BooleanField(source='strategy_id.recommended', read_only=True)
  purchased = serializers.SerializerMethodField()
  expected_time = serializers.CharField(source='strategy_id.expected_time', read_only=True)
  expected_percentage = serializers.CharField(source='strategy_id.expected_percentage', read_only=True)

  class Meta:
    model = UserStrategy
    fields = '__all__'

  def get_purchased(self, obj):
    return obj.purchased()

class ReferralsSerializer(serializers.ModelSerializer):
  referred_user = serializers.SerializerMethodField()

  class Meta:
    model = Referrals
    fields = ['id', 'code', 'referred_user', 'payment_status', 'payment_amount']

  def get_referred_user(self, obj):
    return {'name': obj.referred_user.full_name, 'email': obj.referred_user.email }

class UserCoinSerializer(serializers.ModelSerializer):
  user = serializers.SerializerMethodField()
  coin = serializers.SerializerMethodField()

  class Meta:
    model = UserCoin
    fields = ['id', 'user', 'coin', 'auto_recommended']

  def get_user(self, obj):
    return { 'id': obj.user_id.id, 'name': obj.user_id.full_name, 'email': obj.user_id.email }

  def get_coin(self, obj):
    return { 'id': obj.coin_id.id, 'name': obj.coin_id.name }

class ContactUsSerializer(serializers.ModelSerializer):
  resolved_by_name = serializers.SerializerMethodField()

  class Meta:
    model = ContactUs
    fields = ['id', 'name', 'email', 'subject', 'message', 'resolved', 'mark_as_read', 'created_at', 'resolved_by', 'resolved_by_name']

  def get_resolved_by_name(self, obj):
    return obj.resolved_by.full_name if obj.resolved_by else None
