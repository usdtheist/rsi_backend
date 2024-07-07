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

class Strategy(models.Model):
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=50)
  coin_id = models.ForeignKey(Coin, on_delete=models.CASCADE, related_name='strategies')
  rsi_type = models.IntegerField(null=False)

class  UserStrategy(models.Model):
  id = models.AutoField(primary_key=True)
  user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_strategies')
  strategy_id = models.ForeignKey(Strategy, on_delete=models.CASCADE, related_name='user_strategies')
  enabled = models.BooleanField(default=True)
