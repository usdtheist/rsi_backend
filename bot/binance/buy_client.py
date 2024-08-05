from bot.binance.b_client import BinanceClient

class BuyClient(BinanceClient):
  def __init__(self, api_key, api_secret):
    super().__init__(api_key, api_secret)

  def buySymbol(self, symbol, strategy, logger):
    current_price = self.getPriceOfSymbol(symbol)
    quantity = strategy.amount / current_price
    logger.info(f"You can buy {quantity} BTC with {strategy.amount} USD")

    order = self.order_market_buy(
      symbol=symbol,
      quoteOrderQty=strategy.amount
    )

    logger.info(order)
    return self.create_db_order(order, strategy, amount=strategy.amount)
