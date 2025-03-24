from bot.binance.b_client import BinanceClient
from binance.exceptions import BinanceOrderException, BinanceRequestException, BinanceAPIException

class BuyClient(BinanceClient):
  def __init__(self, api_key, api_secret):
    super().__init__(api_key, api_secret)

  def buySymbol(self, symbol, strategy):
    try:
      current_price = self.getPriceOfSymbol(symbol)
      quantity = strategy.amount / current_price
      print(f"You can buy quantity: {quantity} with {strategy.amount} USD")

      order = self.order_market_buy(
        symbol=symbol,
        quoteOrderQty=strategy.amount
      )
      print(order)

      db_order = self.create_db_order(order, strategy, amount=strategy.amount)

      if db_order and strategy.strategy_id.limited_trades:
        strategy.no_of_trades = strategy.no_of_trades + 1
        strategy.save()

      return {"success": True, "order": db_order}

    except BinanceOrderException as e:
      return {"success": False, "error": f"Order failed: {e}"}
    except BinanceRequestException as e:
      return {"success": False, "error": f"Request error: {e}"}
    except Exception as e:
      return {"success": False, "error": f"Unexpected error: {e}"}
