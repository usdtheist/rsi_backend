from bot.binance.buy_client import BuyClient
from bot.binance.sell_client import SellClient
from api.models import UserStrategy
from bot.models import Order
from django.db.models import Q

def generate_signals(rsi_value_6, rsi_value_14):
  signal = 'HOLD'

  if rsi_value_6 <= 30 or rsi_value_14 <= 30:
    signal = "BUY"
  elif rsi_value_6 >=70 or rsi_value_14 >= 70:
    signal = "SELL"

  return signal

def calculate_rsi(prices, window=14):
  deltas = [prices[i + 1] - prices[i] for i in range(len(prices) - 1)]

  gains = [delta if delta > 0 else 0 for delta in deltas]
  losses = [-delta if delta < 0 else 0 for delta in deltas]

  avg_gain = sum(gains[:window]) / window
  avg_loss = sum(losses[:window]) / window

  if avg_loss == 0:
    rs_values = [float('inf')] * (len(prices) - window)
  else:
    rs_values = [avg_gain / avg_loss]  # Start with first RS value

  for i in range(window, len(gains)):
    avg_gain = ((avg_gain * (window - 1)) + gains[i]) / window
    avg_loss = ((avg_loss * (window - 1)) + losses[i]) / window
    if avg_loss == 0:
      rs_values.append(float('inf'))
    else:
      rs_values.append(avg_gain / avg_loss)

  rsi_values = [100 - (100 / (1 + rs)) if rs != float('inf') else 100 for rs in rs_values]

  return rsi_values[-1]

def fetch_strategies_for_buy(interval, symbol, rsi_6, rsi_14):
  return UserStrategy.objects.filter(
    enabled=True,
    strategy_id__rsi_time=interval,
    strategy_id__coin_id__name=symbol,
    purchased=False
  ).filter(
    Q(strategy_id__rsi_type="6", strategy_id__buy_at__gte=rsi_6) |
    Q(strategy_id__rsi_type="14", strategy_id__buy_at__gte=rsi_14)
  ).distinct()
  
def fetch_strategeis_for_sell(interval, symbol, rsi_6, rsi_14):
  return UserStrategy.objects.filter(
    enabled=True,
    strategy_id__rsi_time=interval,
    strategy_id__coin_id__name=symbol,
    purchased=True,
    sale=False
  ).filter(
    Q(strategy_id__rsi_type="6", strategy_id__sell_at__lte=rsi_6) |
    Q(strategy_id__rsi_type="14", strategy_id__sell_at__lte=rsi_14)
  ).distinct()

def start_trading(rsi_6, rsi_14, interval, symbol):
  signal = generate_signals(rsi_6, rsi_14)

  print(f"Signal ===================>>>>> %s" % signal)

  if signal == 'HOLD':
    return

  strategies = fetch_strategies_for_buy(interval, symbol, rsi_6, rsi_14) if signal == "BUY" else fetch_strategeis_for_sell(interval, symbol, rsi_6, rsi_14)
  print(strategies.values())
  print("Processing ----------------------------------------------------------------")

  if strategies:
    for strategy in strategies:
      user = strategy.user_id
      print(f"Strategy:   {strategy.strategy_id.coin_id.name}: {user.email}: {strategy.strategy_id.name}")
      print(f"start order for user {user.id}")
      print(f"User is eligible for BUY: {strategy.purchased == False and signal == 'BUY'}")
      print(f"User is eligible for SELL: {strategy.purchased == True and strategy.sale == False and signal == 'SELL'}")

      if signal == 'BUY':
        binance_client = BuyClient(user.client_id, user.client_secret)
        order = binance_client.buySymbol(symbol, strategy)
      elif signal == 'SELL':
        binance_client = SellClient(user.client_id, user.client_secret)
        db_orders = Order.objects.filter(
          user_strategy=strategy,
          order_type='BUY',
          parent__isnull=True,
        )
        print('Selling order for user {user.id}')
        order = binance_client.sellSymbol(symbol, strategy, db_orders)
        print('-----------------------------------------------')
        print(f"Sell Order for user {user.id}: {order}")
        print('-----------------------------------------------')
      else:
        order = {}

      print(f"Order for user {user.id}: {order}")

  print("---------------------------------------------------------------- Processed")
  return strategies
