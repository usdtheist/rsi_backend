from rest_framework import serializers
from .models import User, Coin, Strategy, UserStrategy

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = '__all__'

class CoinSerializer(serializers.ModelSerializer):
  class Meta:
    model = Coin
    fields = '__all__'

class StrategySerializer(serializers.ModelSerializer):
  class Meta:
    model = Strategy
    fields = '__all__'

class UserStrategySerializer(serializers.ModelSerializer):
  class Meta:
    model = UserStrategy
    fields = '__all__'
