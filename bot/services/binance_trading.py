from bot.binance.buy_client import BuyClient
from bot.binance.sell_client import SellClient
import concurrent.futures

class BinanceTrading:
  def __init__(self, strategies, signal, symbol):
    self.strategies = strategies
    self.signal = signal
    self.symbol = symbol
    self.execute_strategies_multithreaded()

  def process_strategy(self, strategy, signal, symbol):
    user = strategy.user_id
    print(f"Strategy: {strategy.strategy_id.coin_id.name}: {user.email}: {strategy.strategy_id.name}")
    print(f"start order for user {user.id} {strategy.id}")
    print(f"User is eligible for BUY: {strategy.purchased == False and signal == 'BUY'}  {strategy.id}")
    print(f"User is eligible for SELL: {strategy.purchased == True and signal == 'SELL'}  {strategy.id}")

    if signal == 'BUY' and not strategy.purchased:
      binance_client = BuyClient(user.client_id, user.client_secret)
      order = binance_client.buySymbol(symbol, strategy)
    elif signal == 'SELL' and strategy.purchased:
      binance_client = SellClient(user.client_id, user.client_secret)
      print(f"Selling order for user {user.id}")
      order = binance_client.sellSymbol(symbol, strategy)
      print('-----------------------------------------------')
      print(f"Sell Order for user {user.id}: {order}")
      print('-----------------------------------------------')

    print(f"Order for user {user.id}: {order}")
    return order

  # Execute strategies with controlled threading
  def execute_strategies_multithreaded(self, max_threads=10):
    with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
      futures = [
        executor.submit(self.process_strategy, strategy, self.signal, self.symbol)
        for strategy in self.strategies
      ]
      print('--------------------- here are the futures -----------------------')
      # Wait for all futures to complete
      for future in concurrent.futures.as_completed(futures):
        try:
          result = future.result()  # This is where exceptions will be raised if any occurred
          print(f"Completed strategy execution with result: {result}")
        except Exception as e:
          print(f"Error occurred during strategy execution: {e}")
