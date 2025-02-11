from rest_framework import serializers
from bot.models import Order

class OrderSerializer(serializers.ModelSerializer):
  class Meta:
    model = Order
    fields = '__all__'

class TradeSerializer(serializers.Serializer):
  buy_amount = serializers.FloatField()
  buy_id = serializers.IntegerField()
  buy_date = serializers.DateTimeField()
  buy_strategy_id = serializers.IntegerField()
  buy_price = serializers.DecimalField(max_digits=20, decimal_places=8)
  buy_quantity = serializers.DecimalField(max_digits=20, decimal_places=8)
  buy_commission = serializers.DecimalField(max_digits=20, decimal_places=8)
  sell_id=serializers.IntegerField()
  sell_date = serializers.DateTimeField()
  sell_strategy_id = serializers.IntegerField()
  sell_price = serializers.DecimalField(max_digits=20, decimal_places=8)
  sell_quantity = serializers.DecimalField(max_digits=20, decimal_places=8)
  sell_commission = serializers.DecimalField(max_digits=20, decimal_places=8)
  profit_or_loss = serializers.DecimalField(max_digits=20, decimal_places=8)
  profit_or_loss_percentage = serializers.DecimalField(max_digits=20, decimal_places=8)
  strategy_name  = serializers.CharField()
  coin = serializers.CharField()
