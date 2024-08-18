from api.models import Strategy, UserStrategy

class UserStrategyCreator:
  def __init__(self, user, coin):
    self.user = user
    self.coin = coin
    
  def __strategies(self):
    return Strategy.objects.filter(coin_id=self.coin)    

  def create(self):
    for strategy in self.__strategies():
      UserStrategy.objects.create(user_id=self.user, strategy_id=strategy, enabled=False, amount=5.0)
