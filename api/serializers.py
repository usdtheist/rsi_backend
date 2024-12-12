from rest_framework import serializers
from .models import User, Coin, Strategy, UserStrategy
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework.response import Response

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True, required=True)

  class Meta:
    model = User
    fields = ['email', 'full_name', 'password']

  def create(self, validated_data):
    user = User.objects.create(
      email=validated_data['email'],
      full_name=validated_data['full_name']
    )
    user.set_password(validated_data['password'])
    user.save()

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
    fields = ['id', 'full_name', 'email', 'active', 'active', 'client_id', 'client_secret', 'is_staff', 'payment_receipt_url', 'approved_at', 'role', 'date_joined', 'auto_recommended']

  def get_role(self, obj):
      return 'Admin' if obj.is_staff else 'User'
    
  def update(self, instance, validated_data):
    instance.is_staff = validated_data.get('is_staff', instance.is_staff)
    instance.full_name = validated_data.get('full_name', instance.full_name)
    instance.active = validated_data.get('active', instance.active)
    instance.payment_receipt_url = validated_data.get('payment_receipt_url', instance.payment_receipt_url)
    instance.approved_at = validated_data.get('approved_at', instance.approved_at)
    instance.client_id = validated_data.get('client_id', instance.client_id)
    instance.client_secret = validated_data.get('client_secret', instance.client_secret)
    instance.auto_recommended = validated_data.get('auto_recommended', instance.auto_recommended)
    instance.save()

    return instance

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

  class Meta:
    model = UserStrategy
    fields = '__all__'
