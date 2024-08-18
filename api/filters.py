import django_filters
from .models import UserStrategy

class UserStrategyFilter(django_filters.FilterSet):
  class Meta:
    model = UserStrategy
    fields = ['user_id', 'strategy_id']
