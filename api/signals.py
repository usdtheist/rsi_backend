from django.db.models.signals import pre_save, post_save # type: ignore
from django.dispatch import receiver # type: ignore
from django.core.exceptions import ValidationError # type: ignore
from api.models import Coin, User, UserStrategy, Strategy
from bot.binance.b_client import BinanceClient
from api.services.strategy_creator import StrategyCreator
from api.services.user_strategy_creator import UserStrategyCreator
from api.tasks import setup_user, setup_coin_strategies

@receiver(pre_save, sender=Coin)
def before_save_coin(sender, instance, **kwargs):
  user = User.objects.first()
  if instance.min_value:
    return

  binance_client = BinanceClient(user.client_id, user.client_secret)
  min_notional = binance_client.get_min_notional(instance.name.upper())

  if min_notional == None:
    raise ValidationError('Unable to find min_notional value from binance')
  else:
    instance.min_value = min_notional

@receiver(post_save, sender=User)
def after_save_user(sender, instance, created, **kwargs):
  if created:
    setup_user.delay(instance.id)

@receiver(post_save, sender=Coin)
def after_save_coin(sender, instance, created, **kwargs):
  if not Strategy.objects.filter(coin_id__id=instance.id).exists():
    setup_coin_strategies.delay(instance.id)

@receiver(post_save, sender=Strategy)
def after_save_strategy(sender, instance, **kwargs):
  UserStrategy.objects.filter(strategy_id=instance, user_id__auto_recommended=True).update(enabled=instance.recommended)

@receiver(pre_save, sender=UserStrategy)
def before_save_user_strategy(sender, instance, **kwargs):
  if instance.enabled and instance.amount < instance.strategy_id.coin_id.min_value:
    raise ValidationError(f"Minimum amount should be more than {instance.strategy_id.coin_id.min_value}")

# @receiver(post_save, sender=Strategy)
# def after_save_strategy(sender, instance, created, **kwargs):
#   if created:
#     strategies = Strategy.objects.filter(id=instance.id)
#     if strategies.count() == 1:
#       user = User.objects.first()
#       # asyncio.run(sync_to_async(register_webhook.delay)(user.client_id, user.client_secret, instance.rsi_time, instance.coin_id.name))
