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

    def __str__(self):
        return f'Product code: {self.code}, Product name: {self.name}'

    class Meta:
        ordering = ('-created_at',)


class Stock(Timesteamp):
    """
    A stock model
    """
    product = models.ForeignKey(Product, related_name='stock', on_delete=models.CASCADE)
    units = models.IntegerField()

    def __str__(self):
        return f'Product code: {self.product.code}, Units: {self.units}'

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
    code = models.UUIDField(default=uuid.uuid4, db_index=True, unique=True)  # UUID code by default
    state = models.PositiveSmallIntegerField(choices=OrderStateEnum.choices(),
                                             default=OrderStateEnum.OUTSTANDING.value)
    products = models.ManyToManyField(Product, related_name='orders', through='OrderDetail')
    total = models.FloatField(default=0.0)  # order total

    def __str__(self):
        return f'Order code: {self.code}, State: {self.state}'

    class Meta:
        ordering = ('created_at',)


class OrderDetail(Timesteamp):
    """
    A Order detail model
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='details')
    units = models.IntegerField()
    price = models.FloatField(default=0.0)

    def __str__(self):
        return f'Order code: {self.order.code}, Product code: {self.product.code}, Units: {self.units},' \
               f'Price: {self.price}'

    class Meta:
        ordering = ('created_at',)


class Payment(Timesteamp):
    """
    A Payment model
    """
    orders = models.ManyToManyField(Order, related_name='payments', through='PaymentDetail')
    total = models.FloatField(default=0.0)

    def __str__(self):
        return f'Total: {self.total}'

    class Meta:
        ordering = ('-created_at',)


class PaymentDetail(Timesteamp):
    """
    A Order detail model
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    amount = models.FloatField(default=0.0)

    def __str__(self):
        return f'Amount: {self.amount}'

    class Meta:
        ordering = ('-created_at',)


class Shipment(Timesteamp):
    """
    A Order detail model
    """
    code = models.UUIDField(default=uuid.uuid4, db_index=True, unique=True)  # UUID code by default
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    start_address = models.CharField(max_length=100)
    end_address = models.CharField(max_length=100)

    def __str__(self):
        return f'Start Address: {self.start_address}, End Address: {self.end_address}'

    class Meta:
        ordering = ('-created_at',)


