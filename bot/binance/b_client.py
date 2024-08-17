from binance.enums import *
from binance.client import Client
from django.utils import timezone

class BinanceClient(Client):
  def __init__(self, api_key, api_secret):
    super().__init__(api_key, api_secret)

  def getPriceOfSymbol(self, symbol):
    price_resp = self.get_symbol_ticker(symbol=symbol)
    print(f"The current price of {symbol} is {price_resp} USD")
    return float(price_resp['price'])

  def get_min_notional(self, symbol):
    exchange_info = self.get_exchange_info()
    for s in exchange_info['symbols']:
      if s['symbol'] == symbol:
        for f in s['filters']:
          if f['filterType'] == 'NOTIONAL':
            return float(f['minNotional'])

    return None

  def create_db_order(self, order, user_strategy, amount=None, parentOrders=None):
    from bot.models import Order

    fills = order['fills'][0]

    if order['side'].lower() == 'buy':
      user_strategy.purchased = True
      user_strategy.purchased_at = timezone.now()
      user_strategy.sale = False
      user_strategy.sale_at = None
      user_strategy.save()
    elif order['side'].lower() == 'sell':
      user_strategy.sale = True
      user_strategy.sale_at = timezone.now()
      user_strategy.purchased = False
      user_strategy.purchased_at = None
      user_strategy.save()

    db_order = Order.objects.create(
      external_id=order['orderId'],
      order_type=order['side'],
      amount=amount,
      user_strategy=user_strategy,
      price_unit=fills['price'],
      quantity=order['origQty'],
      commission=fills['commission'],
      external_response = order
    )

    if parentOrders:
      db_order.parent = parentOrders[0]
      db_order.save()

      for order in parentOrders:
        order.parent = db_order
        order.save()

    return db_order


# import logging
# from api.models import *
# from bot.binance.buy_client import BuyClient
# from bot.models import *

# user_strategy = UserStrategy.objects.filter(enabled=True, strategy_id__rsi_time='1m').first()
# user = User.objects.first()
# symbol = 'WUSDT'
# coin = 'WUSDT'
# interval = user_strategy.strategy_id.rsi_time

# logger = logging.getLogger(f"{coin}_{interval}")
# logger.setLevel(logging.INFO)
# handler = logging.FileHandler(f"log/{coin}_{interval}_rsi_values.log")
# handler.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)

# binance_client = BuyClient(user.client_id, user.client_secret)
# strategy = user_strategy

# db_orders = Order.objects.filter(
#   user_strategy=user_strategy,
#   order_type='BUY',
#   parent__isnull=True,
# )
# order = binance_client.sellSymbol(symbol, user_strategy, db_orders, logger)
