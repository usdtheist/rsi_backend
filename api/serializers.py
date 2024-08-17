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
  # strategy_id = StrategySerializer()
  # user_id = UserSerializer()
  strategy_name = serializers.CharField(source='strategy_id.name', read_only=True)

  class Meta:
    model = UserStrategy
    fields = '__all__'
