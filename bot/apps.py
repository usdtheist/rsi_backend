from django.apps import AppConfig

class BotConfig(AppConfig):
  default_auto_field = 'django.db.models.BigAutoField'
  name = 'bot'

  def ready(self):
    from bot.tasks import register_webhook
    from api.models import User, Strategy

    user = User.objects.first()
    uniq_strategies = Strategy.objects.distinct('rsi_time')

    for strategy in uniq_strategies:
      register_webhook.delay(
        user.client_id,
        user.client_secret,
        strategy.rsi_time,
        strategy.coin_id.name
      )
