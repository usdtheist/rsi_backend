import django_filters
from .models import UserStrategy, Strategy, Coin

class UserStrategyFilter(django_filters.FilterSet):
  coin_id = django_filters.NumberFilter(field_name='strategy_id__coin_id')
  
  class Meta:
    model = UserStrategy
    fields = ['user_id', 'strategy_id', 'coin_id']

class StrategyFilter(django_filters.FilterSet):
  class Meta:
    model = Strategy
    fields = ['coin_id']

class CoinFilter(django_filters.FilterSet):
  class Meta:
    model = Coin
    fields = ['enabled']
