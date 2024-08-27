from bot.binance.b_client import BinanceClient
from decimal import Decimal, getcontext, ROUND_DOWN

class SellClient(BinanceClient):
  def __init__(self, api_key, api_secret):
    super().__init__(api_key, api_secret)

  def sellSymbol(self, symbol, strategy, db_orders):
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
    created_order = self.create_db_order(order, strategy, amount=None, parentOrders=db_orders)
    print(created_order)

    return created_order
