from django.db.models import Q
import django_filters
from .models import UserStrategy, Strategy, Coin, Referrals

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

class ReferralsFilter(django_filters.FilterSet):
  search = django_filters.CharFilter(method='filter_search', label='Search')

  class Meta:
    model = Referrals
    fields = ['referrer_id']

  def filter_search(self, queryset, name, value):
    # Use Q objects to search for 'full_name' or 'email' in a case-insensitive way
    return queryset.filter(
      Q(referred_user__full_name__icontains=value) | Q(referred_user__email__icontains=value)
    )
