from bot.binance.b_client import BinanceClient
from binance.exceptions import BinanceOrderException, BinanceRequestException


class BuyClient(BinanceClient):
  def __init__(self, api_key, api_secret):
    super().__init__(api_key, api_secret)

  def buySymbol(self, symbol, strategy):
    try:
      current_price = self.getPriceOfSymbol(symbol)
      quantity = strategy.amount / current_price
      print(f"You can buy {quantity} BTC with {strategy.amount} USD")

      order = self.order_market_buy(
        symbol=symbol,
        quoteOrderQty=strategy.amount
      )
      print(order)

      return self.create_db_order(order, strategy, amount=strategy.amount)
    except BinanceOrderException as e:
      print(f"------------------------------------------------Order failed: {e}------------------------------------------------")
    except BinanceRequestException as e:
      print(f"------------------------------------------------Request error: {e}------------------------------------------------")
    except Exception as e:
      print(f"------------------------------------------------Unexpected error during sell order: {e}------------------------------------------------")
    
    return {}

