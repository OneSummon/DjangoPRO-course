from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet

from .serializers import SubscriptionSerializer
from .models import Subscription


class SubscriptionView(ReadOnlyModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    