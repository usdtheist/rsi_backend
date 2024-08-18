from celery import shared_task
from api.models import Coin, User
from api.services.strategy_creator import StrategyCreator
from api.services.user_strategy_creator import UserStrategyCreator

@shared_task
def setup_user(user_id):
  user = User.objects.get(id=user_id)
  print(f'Setting up user {user.full_name}')

  coins = Coin.objects.all()

  for coin in coins:
    print(f'Creating strategy for {coin.name}')
    UserStrategyCreator(user, coin).create()

@shared_task
def setup_coin_strategies(coin_id):
  coin = Coin.objects.get(id=coin_id)
  print(f'Coin is {coin.name}')
  StrategyCreator(coin).create()

  users = User.objects.all()

  for user in users:
    print(f'Creating strategy for user {user.full_name}')
    UserStrategyCreator(user, coin).create()
