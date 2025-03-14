from django.db.models.signals import pre_save, post_save # type: ignore
from django.dispatch import receiver # type: ignore
from django.core.exceptions import ValidationError # type: ignore
from api.models import Coin, User, UserStrategy, Strategy, UserCoin
from bot.binance.b_client import BinanceClient
from api.tasks import setup_user, setup_coin_strategies

from rsi_project.mail.backend.smtp import send_mail
from django.template.loader import render_to_string

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
    html_content = render_to_string('emails/welcome_email.html', {'user': instance})
    send_mail("Welcome to USDTHEIST family", instance.email, html_content)

    admin_users = list(User.objects.filter(is_staff=True).values_list('email', flat=True))
    html_content = render_to_string('emails/admin/new_user_registration_email.html', {'user': instance})
    send_mail("New member has joined the USDTHEIST family", admin_users[0], html_content, cc_recipients=[admin_users[1:]])

    setup_user.delay(instance.id)

    coins = Coin.objects.all()
    for coin in coins:
      UserCoin.objects.create(coin_id=coin, user_id=instance)

@receiver(post_save, sender=Coin)
def after_save_coin(sender, instance, created, **kwargs):
  if not Strategy.objects.filter(coin_id__id=instance.id).exists():
    setup_coin_strategies.delay(instance.id)

  if not UserCoin.objects.filter(coin_id__id=instance.id).exists():
    users = User.objects.all()
    for user in users:
      UserCoin.objects.create(coin_id=instance, user_id=user)

@receiver(post_save, sender=Strategy)
def after_save_strategy(sender, instance, **kwargs):
  if not instance.limited_trades:
    print(instance.name, instance.limited_trades)
    user_strategies = UserStrategy.objects.filter(no_of_trades__gte=1, strategy_id=instance)
    user_strategies.update(no_of_trades=0)
  user_coins = UserCoin.objects.filter(coin_id=instance.coin_id, auto_recommended=True)
  for user_coin in user_coins:
    strategies = UserStrategy.objects.filter(user_id=user_coin.user_id, strategy_id=instance)
    strategies.update(enabled=instance.recommended)

@receiver(pre_save, sender=UserStrategy)
def before_save_user_strategy(sender, instance, **kwargs):
  # from channels.layers import get_channel_layer
  # from asgiref.sync import async_to_sync

  # channel_layer = get_channel_layer()
  # print('----------------------------------------------------------------')
  # async_to_sync(channel_layer.group_send)(
  #       'chat_global_chat',
  #     {"type": "chat_message", "message": "Hello from Django! Hashim is here"}
  # )
  # print('----------------------------------------------------------------')
  if instance.enabled and instance.amount < instance.strategy_id.coin_id.min_value:
    raise ValidationError(f"Minimum amount should be more than {instance.strategy_id.coin_id.min_value}")

# @receiver(post_save, sender=Strategy)
# def after_save_strategy(sender, instance, created, **kwargs):
#   if created:
#     strategies = Strategy.objects.filter(id=instance.id)
#     if strategies.count() == 1:
#       user = User.objects.first()
#       # asyncio.run(sync_to_async(register_webhook.delay)(user.client_id, user.client_secret, instance.rsi_time, instance.coin_id.name))
