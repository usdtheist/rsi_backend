from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import get_random_string
from .managers import CustomUserManager

class User(AbstractBaseUser, PermissionsMixin):
  id = models.AutoField(primary_key=True)
  full_name = models.CharField(max_length=100)
  email = models.EmailField(_("email address"), unique=True)
  active = models.BooleanField(default=False)
  is_staff = models.BooleanField(default=False)
  client_secret = models.CharField(max_length=100, null=True, blank=True)
  client_id = models.CharField(max_length=100, null=True, blank=True)
  date_joined = models.DateTimeField(auto_now_add=True)
  payment_receipt_url = models.URLField(blank=True, null=True)
  profile_image_url = models.URLField(blank=True, null=True)
  approved_at = models.DateTimeField(null=True, blank=True)
  auto_recommended = models.BooleanField(default=False)
  referral_code = models.CharField(max_length=20, null=True, blank=True)
  phone_number = models.CharField(max_length=16, null=True, blank=True)
  whatsapp_number = models.CharField(max_length=16, null=True, blank=True)
  wallet_address = models.CharField(max_length=50, null=True, blank=True)

  USERNAME_FIELD = "email"
  REQUIRED_FIELDS = []

  objects = CustomUserManager()

  def save(self, *args, **kwargs):
    if not self.referral_code:
      self.referral_code = get_random_string(10, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    super().save(*args, **kwargs)

  def __str__(self):
    return self.email

class Referrals(models.Model):
  code = models.CharField(max_length=20, null=False)
  referred_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="referred_user")
  referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="referral_history")

  payment_status = models.CharField(max_length=10, null=False, blank=True, default='pending')
  payment_amount = models.DecimalField(max_digits=5, decimal_places=2, null=False, blank=True, default=10.0)

  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    unique_together = ('code', 'referred_user')

class Coin(models.Model):
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=50, unique=True)
  asset = models.CharField(max_length=50, default='USDT')
  base_name = models.CharField(max_length=50, default='W')
  min_value = models.FloatField(null=True, default=0)
  recommended = models.BooleanField(default=False)
  enabled = models.BooleanField(default=False)
  bottom_value = models.DecimalField(null=False, default=0.0, max_digits=10, decimal_places=5)

  class Meta:
    indexes = [
      models.Index(fields=["name"]),
    ]

class UserCoin(models.Model):
  id = models.AutoField(primary_key=True)
  user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_coins')
  coin_id = models.ForeignKey(Coin, on_delete=models.CASCADE, related_name='user_coins')
  auto_recommended = models.BooleanField(default=False)

class Strategy(models.Model):
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=50, unique=True)
  coin_id = models.ForeignKey(Coin, on_delete=models.CASCADE, related_name='strategies')
  rsi_type = models.IntegerField(null=False)
  rsi_time = models.CharField(max_length=10, null=False, default='1m')
  buy_at = models.IntegerField(null=False, default=30)
  sell_at = models.IntegerField(null=False, default=70)
  recommended = models.BooleanField(default=False)
  order = models.IntegerField(null=True)
  expected_time = models.CharField(null=False, max_length=20, default="1 hours")
  expected_percentage = models.CharField(max_length=20, null=False, default="0.25%")

  class Meta:
    constraints = [
      models.UniqueConstraint(fields=['name', 'coin_id'], name='unique_name_coin_id')
    ]

class UserStrategy(models.Model):
  id = models.AutoField(primary_key=True)
  user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_strategies')
  strategy_id = models.ForeignKey(Strategy, on_delete=models.CASCADE, related_name='user_strategies')
  enabled = models.BooleanField(default=True)
  amount = models.FloatField(null=False, default=10.0, validators=[MinValueValidator(10.0)])

  class Meta:
    ordering = ['strategy_id__order']
    constraints = [
      models.UniqueConstraint(fields=['user_id','strategy_id'], name='unique_user_strategy_id')
    ]

  def purchased(self):
    from bot.models import Order

    return Order.objects.filter(
      user_strategy_id=self.id,
      order_type='BUY',
      parent_id__isnull=True
    ).exists()

class ContactUs(models.Model):
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=100, null=False)
  email = models.EmailField(max_length=100, null=False)
  subject = models.CharField(max_length=200, null=False)
  message = models.TextField(null=False)
  resolved = models.BooleanField(default=False)
  mark_as_read = models.BooleanField(default=False)
  resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='resolved_reports', null=True)

  created_at = models.DateTimeField(auto_now_add=True)
