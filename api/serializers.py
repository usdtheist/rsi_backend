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
  # coin_id = CoinSerializer()

  class Meta:
    model = Strategy
    fields = '__all__'

class UserStrategySerializer(serializers.ModelSerializer):
  strategy_name = serializers.CharField(source='strategy_id.name', read_only=True)
  rsi_type = serializers.CharField(source='strategy_id.rsi_type', read_only=True)
  rsi_time = serializers.CharField(source='strategy_id.rsi_time', read_only=True)

  class Meta:
    model = UserStrategy
    fields = '__all__'
