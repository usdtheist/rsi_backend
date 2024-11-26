import django_filters
from .models import Order

class OrderFilter(django_filters.FilterSet):
  user_id = django_filters.NumberFilter(field_name='user_strategy_id__user_id')
  coin_id = django_filters.NumberFilter(field_name='user_strategy_id__strategy_id__coin_id')

  class Meta:
    model = Order
    fields = ['user_strategy', 'parent', 'user_id', 'coin_id']
