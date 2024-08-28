from bot.binance.b_client import BinanceClient
from decimal import Decimal
from binance.exceptions import BinanceOrderException, BinanceRequestException

class SellClient(BinanceClient):
  def __init__(self, api_key, api_secret):
    super().__init__(api_key, api_secret)

  def sellSymbol(self, symbol, strategy, db_orders):
    try:
      quantity = Decimal(0)
      for db_order in db_orders:
        quantity += Decimal(db_order.quantity)

      current_price = self.getPriceOfSymbol(symbol)
      usd_amount = quantity * Decimal(current_price)
      usd_amount = '{:.8f}'.format(usd_amount)
      print(f"You can sell {usd_amount} with quantity: {quantity}")

      print(f"Sell symbol for {quantity}")
      order = self.order_market_sell(symbol=symbol,quoteOrderQty=usd_amount)
      print(order)
      self.create_db_order(order, strategy, amount=None, parentOrders=db_orders)

    except BinanceOrderException as e:
      print(f"------------------------------------------------Order failed: {e}------------------------------------------------")
    except BinanceRequestException as e:
      print(f"------------------------------------------------Request error: {e}------------------------------------------------")
    except Exception as e:
      print(f"------------------------------------------------Unexpected error during sell order: {e}------------------------------------------------")

    return {}
