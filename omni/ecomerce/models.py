import uuid

from django.db import models

from ecomerce.enums import ProductCategoryEnum, OrderStateEnum
from tracking.models import Timesteamp


class Product(Timesteamp):
    """
    A Product model
    """
    code = models.CharField(max_length=10, unique=True, db_index=True)  # unique code
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300, null=True, blank=True)
    category = models.SmallIntegerField(choices=ProductCategoryEnum.choices())
    price = models.PositiveIntegerField()

    class Meta:
        ordering = ('-created_at',)


class Stock(Timesteamp):
    """
    A stock model
    """
    product = models.ForeignKey(Product, related_name='stock', on_delete=models.CASCADE)
    units = models.IntegerField()

    def have_enough_units(self, units: int) -> bool:
        """
        Check if this product have available stock
        :return: True if have stock, False otherwise
        """
        return self.units >= units

    class Meta:
        ordering = ('-modified_at',)


class Order(Timesteamp):
    """
    A Order model
    """
    code = models.UUIDField(default=uuid.uuid4(), db_index=True, unique=True)  # UUID code by default
    state = models.PositiveSmallIntegerField(choices=OrderStateEnum.choices(),
                                             default=OrderStateEnum.OUTSTANDING.value)
    products = models.ManyToManyField(Product, related_name='orders')
    total = models.FloatField(default=0.0)

    class Meta:
        ordering = ('-created_at',)


class Payment(Timesteamp):
    """
    A Payment model
    """
    orders = models.ManyToManyField(Order, related_name='payments')
    total = models.FloatField(default=0.0)

    class Meta:
        ordering = ('-created_at',)


