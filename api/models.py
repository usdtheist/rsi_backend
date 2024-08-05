from django.db import models

class User(models.Model):
  id = models.AutoField(primary_key=True)
  full_name = models.CharField(max_length=100)
  email = models.EmailField(max_length=50, unique=True)
  client_secret = models.CharField(max_length=100)
  client_id = models.CharField(max_length=100)

class Coin(models.Model):
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=50)
  min_value = models.FloatField(null=True, default=0)

class Strategy(models.Model):
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=50)
  coin_id = models.ForeignKey(Coin, on_delete=models.CASCADE, related_name='strategies')
  rsi_type = models.IntegerField(null=False)
  rsi_time = models.CharField(max_length=10, null=False, default='1m')

class UserStrategy(models.Model):
  id = models.AutoField(primary_key=True)
  user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_strategies')
  strategy_id = models.ForeignKey(Strategy, on_delete=models.CASCADE, related_name='user_strategies')
  enabled = models.BooleanField(default=True)
  purchased = models.BooleanField(null=False, default=False)
  purchased_at = models.DateTimeField(null=True)
  sale = models.BooleanField(null=False, default=False)
  sale_at = models.DateTimeField(null=True)
  amount = models.FloatField(null=False, default=0)

# DAAPS - Decentralized walets/ decentralized exchanges/ 