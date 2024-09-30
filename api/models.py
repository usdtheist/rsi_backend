from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager

class User(AbstractBaseUser, PermissionsMixin):
  id = models.AutoField(primary_key=True)
  full_name = models.CharField(max_length=100)
  email = models.EmailField(_("email address"), unique=True)
  active = models.BooleanField(default=False)
  is_staff = models.BooleanField(default=False)
  client_secret = models.CharField(max_length=100, null=True, blank=True)
  client_id = models.CharField(max_length=100, null=True, blank=True)
  date_joined = models.DateTimeField(default=timezone.now)
  payment_receipt_url = models.URLField(blank=True, null=True)
  approved_at = models.DateTimeField(null=True, blank=True)

  USERNAME_FIELD = "email"
  REQUIRED_FIELDS = []
  
  objects = CustomUserManager()
  
  def __str__(self):
    return self.email

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
  buy_at = models.IntegerField(null=False, default=30)
  sell_at = models.IntegerField(null=False, default=70)
  
  class Meta:
    constraints = [
      models.UniqueConstraint(fields=['name', 'coin_id'], name='unique_name_coin_id')
    ]

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
  
  class Meta:
    constraints = [
      models.UniqueConstraint(fields=['user_id','strategy_id'], name='unique_user_strategy_id')
    ]
