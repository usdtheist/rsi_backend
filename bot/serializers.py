from rest_framework import serializers
from bot.models import Order

class OrderSerializer(serializers.ModelSerializer):
  class Meta:
    model = Order
    fields = '__all__'

class TradeSerializer(serializers.Serializer):
  buy_id = serializers.IntegerField()
  buy_strategy_id = serializers.IntegerField()
  buy_price = serializers.DecimalField(max_digits=20, decimal_places=8)
  buy_quantity = serializers.DecimalField(max_digits=20, decimal_places=8)
  buy_commission = serializers.DecimalField(max_digits=20, decimal_places=8)
  sell_id=serializers.IntegerField()
  sell_strategy_id = serializers.IntegerField()
  sell_price = serializers.DecimalField(max_digits=20, decimal_places=8)
  sell_quantity = serializers.DecimalField(max_digits=20, decimal_places=8)
  sell_commission = serializers.DecimalField(max_digits=20, decimal_places=8)
  profit_or_loss = serializers.DecimalField(max_digits=20, decimal_places=8)
