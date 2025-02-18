from bot.binance.b_client import BinanceClient
from decimal import Decimal
from bot.models import Order
from binance.exceptions import BinanceOrderException, BinanceRequestException

class SellClient(BinanceClient):
  def __init__(self, api_key, api_secret):
    super().__init__(api_key, api_secret)

  def sellSymbol(self, symbol, strategy):
    try:
      db_order = Order.objects.filter(
        user_strategy=strategy,
        order_type='BUY',
        parent__isnull=True,
        status='pending',
      ).first()

      print(f"here is the pending order that is going to sold {db_order}")
      db_order.status = 'in_progress'
      db_order.save()

      quantity = Decimal(db_order.quantity)

      current_price = self.getPriceOfSymbol(symbol)
      usd_amount = quantity * Decimal(current_price)
      usd_amount = '{:.8f}'.format(usd_amount)
      print(f"You can sell {usd_amount} with quantity: {quantity}")

      print(f"Sell symbol for {quantity}")
      order = self.order_market_sell(symbol=symbol,quoteOrderQty=usd_amount)

      db_order = self.create_db_order(order, strategy, amount=None, buyOrder=db_order)
      return {"success": True, "order": db_order}

    except BinanceOrderException as e:
      db_order.status = 'pending'
      db_order.save()
      return {"success": False, "error": f"Order failed: {e}"}
    except BinanceRequestException as e:
      db_order.status = 'pending'
      db_order.save()
      return {"success": False, "error": f"Request error: {e}"}
    except Exception as e:
      db_order.status = 'pending'
      db_order.save()
      return {"success": False, "error": f"Unexpected error: {e}"}
