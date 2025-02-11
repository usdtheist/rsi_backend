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

  def get_coins(self):
    exchange_info = self.get_exchange_info()
    return [
      {
        'name': coin['symbol'],
        'base_name': coin['baseAsset'],
        'asset': coin['quoteAsset'],
      }

      for coin in exchange_info['symbols']
      if coin['quoteAsset'] == 'USDT'
    ]

  def fetch_account(self, **params):
    account_info = self.get_account(**params)
    for balance in account_info["balances"]:
      asset = balance["asset"]
      free = balance["free"]
      locked = balance["locked"]

      if free > 0 or locked > 0:
        print(f"Asset: {asset}, Free: {free}, Locked: {locked}")

  def get_min_notional(self, symbol):
    exchange_info = self.get_exchange_info()
    for s in exchange_info['symbols']:
      if s['symbol'] == symbol:
        for f in s['filters']:
          if f['filterType'] == 'NOTIONAL':
            return float(f['minNotional'])

    return None

  def create_db_order(self, order, user_strategy, amount=None, buyOrder=None):
    from bot.models import Order

    sell_order = Order.objects.create(
      external_id=order['orderId'],
      order_type=order['side'],
      amount=amount,
      user_strategy=user_strategy,
      price_unit=order['fills'][0]['price'],
      quantity=order['origQty'],
      commission=sum([float(fill['commission']) for fill in order['fills']]),
      external_response = order,
      status='pending' if order['side'].lower() == 'buy' else 'completed'
    )

    if buyOrder:
      buyOrder.parent = sell_order
      buyOrder.status = 'completed'
      buyOrder.save()

    return sell_order
