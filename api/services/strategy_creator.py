from api.models import Strategy

class StrategyCreator:
  def __init__(self, coin, **kwargs):
    self.coin = coin

  def create(self):
    for strategy_data in self.__strategy_list():
      Strategy.objects.create(**strategy_data)

  def __strategy_list(self):
    return [
      { "name": "Strategy 1", "rsi_type": "6", "rsi_time": "1m", "coin_id": self.coin },
      { "name": "Strategy 2", "rsi_type": "14", "rsi_time": "1m", "coin_id": self.coin },
      { "name": "Strategy 3", "rsi_type": "6", "rsi_time": "3m", "coin_id": self.coin },
      { "name": "Strategy 4", "rsi_type": "14", "rsi_time": "3m", "coin_id": self.coin },
      { "name": "Strategy 5", "rsi_type": "6", "rsi_time": "5m", "coin_id": self.coin },
      { "name": "Strategy 6", "rsi_type": "14", "rsi_time": "5m", "coin_id": self.coin },
      { "name": "Strategy 7", "rsi_type": "6", "rsi_time": "15m", "coin_id": self.coin },
      { "name": "Strategy 8", "rsi_type": "14", "rsi_time": "15m", "coin_id": self.coin },
      { "name": "Strategy 9", "rsi_type": "6", "rsi_time": "30m", "coin_id": self.coin },
      { "name": "Strategy 10", "rsi_type": "14", "rsi_time": "30m", "coin_id": self.coin },
      { "name": "Strategy 11", "rsi_type": "6", "rsi_time": "1h", "coin_id": self.coin },
      { "name": "Strategy 12", "rsi_type": "14", "rsi_time": "1h", "coin_id": self.coin },
      { "name": "Strategy 13", "rsi_type": "6", "rsi_time": "2h", "coin_id": self.coin },
      { "name": "Strategy 14", "rsi_type": "14", "rsi_time": "2h", "coin_id": self.coin },
      { "name": "Strategy 15", "rsi_type": "6", "rsi_time": "4h", "coin_id": self.coin },
      { "name": "Strategy 16", "rsi_type": "14", "rsi_time": "4h", "coin_id": self.coin },
      { "name": "Strategy 17", "rsi_type": "6", "rsi_time": "6h", "coin_id": self.coin },
      { "name": "Strategy 18", "rsi_type": "14", "rsi_time": "6h", "coin_id": self.coin },
      { "name": "Strategy 19", "rsi_type": "6", "rsi_time": "8h", "coin_id": self.coin },
      { "name": "Strategy 20", "rsi_type": "14", "rsi_time": "8h", "coin_id": self.coin },
      { "name": "Strategy 21", "rsi_type": "6", "rsi_time": "12h", "coin_id": self.coin },
      { "name": "Strategy 22", "rsi_type": "14", "rsi_time": "12h", "coin_id": self.coin },
      { "name": "Strategy 23", "rsi_type": "6", "rsi_time": "1d", "coin_id": self.coin },
      { "name": "Strategy 24", "rsi_type": "14", "rsi_time": "1d", "coin_id": self.coin },
      { "name": "Strategy 25", "rsi_type": "6", "rsi_time": "3d", "coin_id": self.coin },
      { "name": "Strategy 26", "rsi_type": "14", "rsi_time": "3d", "coin_id": self.coin },
      { "name": "Strategy 27", "rsi_type": "6", "rsi_time": "1w", "coin_id": self.coin },
      { "name": "Strategy 28", "rsi_type": "14", "rsi_time": "1w", "coin_id": self.coin },
      { "name": "Strategy 29", "rsi_type": "6", "rsi_time": "1M", "coin_id": self.coin },
      { "name": "Strategy 30", "rsi_type": "14", "rsi_time": "1M", "coin_id": self.coin }
    ]
