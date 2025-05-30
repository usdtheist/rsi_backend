from django.db import models
from api.models import User

class Order(models.Model):
  CHOICES =  [
    ('BUY', 'Buy'),
    ('SELL', 'Sell'),
  ]

  id = models.AutoField(primary_key=True)
  external_id = models.CharField(max_length=20, blank=True, null=True)
  amount = models.FloatField(null=True, blank=True)
  order_type = models.CharField(max_length=5, choices=CHOICES)
  user_strategy = models.ForeignKey('api.UserStrategy', on_delete=models.CASCADE)
  price_unit = models.CharField(max_length=20, blank=True, null=True)
  quantity = models.CharField(max_length=20, blank=True, null=True)
  commission = models.CharField(max_length=20, blank=True, null=True)
  external_response = models.JSONField(null=True, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sell_order')
  status = models.CharField(max_length=20, null=False, default='pending')
  user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)

  def save(self, *args, **kwargs):
    if not self.user:
      self.user = self.user_strategy.user_id
    super().save(*args, **kwargs)
