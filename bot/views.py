from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.db.models.functions import Cast
from bot.models import Order
from api.models import UserStrategy, Coin
from bot.serializers import OrderSerializer, TradeSerializer
from bot.filters import OrderFilter
from bot.binance.buy_client import BuyClient
from bot.binance.sell_client import SellClient
from rest_framework.permissions import IsAuthenticated

class OrderViewSet(viewsets.ModelViewSet):
  queryset = Order.objects.all()
  serializer_class = OrderSerializer
  filter_backends = [DjangoFilterBackend]
  filterset_class = OrderFilter

class TradeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
  permission_classes = [IsAuthenticated]

  def get_queryset(self):

    queryset = Order.objects.filter(
                  order_type='BUY',
                ).annotate(
                  strategy_name=F('user_strategy_id__strategy_id__name'),
                  coin=F('user_strategy_id__strategy_id__coin_id__name'),
                  buy_amount=F('amount'),
                  buy_id=F('id'),
                  buy_date=F('created_at'),
                  sell_id=F('parent__id'),
                  sell_date=F('parent__created_at'),
                  buy_price=Cast(F('price_unit'), DecimalField(max_digits=20, decimal_places=8)),
                  buy_commission=Cast(F('commission'), DecimalField(max_digits=20, decimal_places=8)),
                  sell_price=Cast(F('parent__price_unit'), DecimalField(max_digits=20, decimal_places=8)),
                  sell_commission=Cast(F('parent__commission'), DecimalField(max_digits=20, decimal_places=8)),
                  buy_strategy_id=F('user_strategy_id'),
                  sell_strategy_id=F('parent__user_strategy_id'),
                  buy_quantity=Cast(F('quantity'), DecimalField(max_digits=20, decimal_places=8)),
                  sell_quantity=Cast(F('parent__quantity'), DecimalField(max_digits=20, decimal_places=8)),
                  profit_or_loss=ExpressionWrapper(
                    ((F('sell_price') * F('sell_quantity')) - F('sell_commission')) - F('amount'),
                    output_field=DecimalField(max_digits=20, decimal_places=8)
                  )
                ).order_by('-created_at'
                ).values(
                  'buy_id', 'sell_id', 'buy_date', 'sell_date', 'buy_price', 'sell_price', 'buy_quantity', 'sell_quantity', 'profit_or_loss',
                  'buy_commission', 'sell_price', 'buy_strategy_id', 'sell_strategy_id', 'sell_commission', 'buy_amount', 'strategy_name',
                  'coin'
                )

    strategy_id = self.request.query_params.get('strategy_id', None)
    user_id = self.request.query_params.get('user_id', None)
    coin_id = self.request.query_params.get('coin_id', None)
    if strategy_id:
      queryset = queryset.filter(user_strategy_id=strategy_id)
    if user_id:
      queryset = queryset.filter(user_id=user_id)
    if coin_id:
      queryset = queryset.filter(user_strategy_id__strategy_id__coin_id=coin_id)

    return queryset

  def list(self, request, *args, **kwargs):
    queryset = self.get_queryset()
    serializer = TradeSerializer(queryset, many=True)
    return Response(serializer.data)
  
  @action(detail=False, methods=['get'], url_path='count')
  def count(self, request, *args, **kwargs):
    queryset = self.get_queryset()

    total_profit_or_loss = queryset.aggregate(total_profit_or_loss=Sum('profit_or_loss'))
    total_investment = queryset.aggregate(total_investment=Sum(F('amount')))
    return Response({'total': total_profit_or_loss, 'total_investment': total_investment})

  @action(detail=False, methods=['get'], url_path='buy')
  def buy(self, request, *args, **kwargs):
    print(request.query_params)
    user = self.request.user
    user_strategy = UserStrategy.objects.get(id=request.query_params['user_strategy_id'])
    coin = Coin.objects.get(id=request.query_params['coin_id'])

    binance_client = BuyClient(user.client_id, user.client_secret)
    response = binance_client.buySymbol(coin.name, user_strategy)

    if not response['success']:
      return Response(response['error'], status=422)

    serializer = OrderSerializer(response['order'])
    return Response(serializer.data, status=status.HTTP_200_OK)
  
  @action(detail=False, methods=['get'], url_path='sell')
  def sell(self, request, *args, **kwargs):
    print(request.query_params)
    user = self.request.user
    user_strategy = UserStrategy.objects.get(id=request.query_params['user_strategy_id'])
    coin = Coin.objects.get(id=request.query_params['coin_id'])

    binance_client = SellClient(user.client_id, user.client_secret)
    response = binance_client.sellSymbol(coin.name, user_strategy)
   
    if not response['success']:
      return Response(response['error'], status=422)

    serializer = OrderSerializer(response['order'])
    return Response(serializer.data, status=status.HTTP_200_OK)
 