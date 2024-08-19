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

  closed_klines = GetKliesApi(api_key, secret_key, interval=interval).run()
  socket_url = f"wss://stream.binance.com:9443/ws/{coin.lower()}@kline_{interval}"
  client = WebSocketClient(socket_url, closed_klines, interval=interval, coin=coin)
  client.run()

@worker_ready.connect
def at_startup(sender, **kwargs):
  from api.models import User, Strategy

  user = User.objects.first()
  uniq_strategies = Strategy.objects.distinct('rsi_time')

  for strategy in uniq_strategies:
    if not is_task_active_or_scheduled('bot.tasks.register_webhook', [user.client_id, user.client_secret, strategy.rsi_time, strategy.coin_id.name]):
      print(f"Registering webhook for {strategy.coin_id.name} at {strategy.rsi_time} interval")
      register_webhook.delay(
        user.client_id,
        user.client_secret,
        strategy.rsi_time,
        strategy.coin_id.name
      )

def is_task_running(task_name, task_args):
  i = app.control.inspect()
  active_tasks = i.active()

  if active_tasks:
    for worker, tasks in active_tasks.items():
      for task in tasks:
        if task['name'] == task_name and task['args'] == str(task_args):
          return True
  return False

def is_task_scheduled(task_name, task_args):
  i = app.control.inspect()
  scheduled_tasks = i.reserved()

  if scheduled_tasks:
    for worker, tasks in scheduled_tasks.items():
      for task in tasks:
        if task['name'] == task_name and task['args'] == task_args:
          return True
  return False

def is_task_active_or_scheduled(task_name, task_args):
  return is_task_running(task_name, task_args) or is_task_scheduled(task_name, task_args)
