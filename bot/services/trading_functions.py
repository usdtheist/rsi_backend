from api.models import UserStrategy
from django.db.models import Q, Exists, OuterRef
from bot.models import Order
from bot.services.binance_trading import BinanceTrading

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
    user_id__active=True,
    enabled=True,
    strategy_id__rsi_time=interval,
    strategy_id__coin_id__name=symbol
  ).annotate(
    purchased=Exists(
      Order.objects.filter(
        user_strategy__id=OuterRef('id'),
        order_type='BUY',
        parent_id__isnull=True
      )
    )
  ).filter(
    Q(strategy_id__rsi_type="6", strategy_id__buy_at__gte=rsi_6) |
    Q(strategy_id__rsi_type="14", strategy_id__buy_at__gte=rsi_14)
  ).filter(
    purchased=False
  ).distinct()

def fetch_strategeis_for_sell(interval, symbol, rsi_6, rsi_14):
  return UserStrategy.objects.filter(
    user_id__active=True,
    enabled=True,
    strategy_id__rsi_time=interval,
    strategy_id__coin_id__name=symbol
  ).annotate(
    purchased=Exists(
      Order.objects.filter(
        user_strategy_id=OuterRef('id'),
        order_type='BUY',
        parent_id__isnull=True
      )
    )
  ).filter(
    purchased=True
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
    BinanceTrading(strategies, signal, symbol)

  print("---------------------------------------------------------------- Processed")
  return strategies
