import django_filters
from .models import UserStrategy

class UserStrategyFilter(django_filters.FilterSet):
  coin_id = django_filters.NumberFilter(field_name='strategy_id__coin_id')
  
  class Meta:
    model = UserStrategy
    fields = ['user_id', 'strategy_id', 'coin_id']
