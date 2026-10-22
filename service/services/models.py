from django.db import models, transaction
from django.core.validators import MaxValueValidator

from clients.models import Client
from services.tasks import set_comment, set_price

class Service(models.Model):
    name = models.CharField(max_length=50)
    full_price = models.PositiveBigIntegerField()

    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.__full_price = self.full_price
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.full_price != self.__full_price:
            for subscription in self.subscriptions.all():
                transaction.on_commit(lambda: set_price.delay(subscription.id))


class Plan(models.Model):
    PLAN_TYPES = (
        ('full', 'Full'),
        ('student', 'Student'),
        ('discount', 'Discount'),
    )

    plan_type = models.CharField(choices=PLAN_TYPES, max_length=10)
    discount_percent = models.PositiveBigIntegerField(default=0, validators=[
        MaxValueValidator(100)
    ])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__discount_percent = self.discount_percent

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
        if self.discount_percent != self.__discount_percent:
            for subscription in self.subscriptions.all():
                transaction.on_commit(lambda: set_price.delay(subscription.id))
                transaction.on_commit(lambda: set_comment.delay(subscription.id))


class Subscription(models.Model):
    client = models.ForeignKey(Client, related_name='subscriptions', on_delete=models.PROTECT)
    service = models.ForeignKey(Service, related_name='subscriptions', on_delete=models.PROTECT)
    plan = models.ForeignKey(Plan, related_name='subscriptions', on_delete=models.PROTECT)
    price = models.PositiveBigIntegerField(default=0)
    comment = models.CharField(max_length=50, default='')
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        transaction.on_commit(lambda: set_price.delay(self.id))