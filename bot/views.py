from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from bot.models import Order
from bot.serializers import OrderSerializer
from bot.filters import OrderFilter

class OrderViewSet(viewsets.ModelViewSet):
  queryset = Order.objects.all()
  serializer_class = OrderSerializer
  filter_backends = [DjangoFilterBackend]
  filterset_class = OrderFilter
