# celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.signals import worker_ready # type: ignore

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rsi_project.settings')

app = Celery('rsi_project')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Task for registering webhooks
@app.task
def register_webhook(api_key, secret_key, interval, coin):
  from bot.services.webhook import WebSocketClient
  from bot.services.klines_api import GetKliesApi

  closed_klines = GetKliesApi(api_key, secret_key, pair=coin, interval=interval).run()
  socket_url = f"wss://stream.binance.com:9443/ws/{coin.lower()}@kline_{interval}"
  client = WebSocketClient(socket_url, closed_klines, interval=interval, coin=coin)
  client.run()

@app.task
def fetch_coins():
  from api.models import User, Coin
  from bot.binance.b_client import BinanceClient

  user = User.objects.first()
  client = BinanceClient(user.client_id, user.client_secret)
  coins = client.get_coins()

  print('Coins fetched')

  for coin in coins:
    existing_coin = Coin.objects.get(name=coin['name'])

    if existing_coin:
      existing_coin.base_name = coin['base_name']
      existing_coin.asset = coin['asset']
      existing_coin.save()
    else:
      Coin.objects.create(**coin)

  print('Coins updated/created')

@worker_ready.connect
def at_startup(sender, **kwargs):
  fetch_coins.delay()

  from api.models import User, Strategy

  user = User.objects.first()
  uniq_strategies = Strategy.objects.filter(coin_id__enabled=True).distinct('rsi_time', 'coin_id')

  for strategy in uniq_strategies:
    print(f"Registering webhook for {strategy.coin_id.name} at {strategy.rsi_time} interval")
    register_webhook.delay(
      user.client_id,
      user.client_secret,
      strategy.rsi_time,
      strategy.coin_id.name
    )
