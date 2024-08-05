from rest_framework import viewsets
from bot.models import Order
from bot.serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
  queryset = Order.objects.all()
  serializer_class = OrderSerializer
