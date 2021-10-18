import logging
import traceback
from typing import Dict, List, Any

from django.db import IntegrityError, transaction

from ecomerce.enums import OrderStateEnum
from ecomerce.models import Product, Stock, Order, Payment, OrderDetail, PaymentDetail, Shipment

logger = logging.getLogger(__name__)


class OmniException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f'Exception message: {self.message}'


@transaction.atomic()
def add_product_in_stock(**kwargs: Dict[str, str]) -> Product:
    """
    Add a product inside db
    :param kwargs: Product information
    :return: Product added
    """
    try:
        product = Product.objects.create(code=kwargs['code'].strip(), name=kwargs['name'].strip(),
                                         price=kwargs['price'], category=kwargs['category'],
                                         description=kwargs['description'])
        Stock.objects.create(product=product, units=kwargs['units'])
        return product
    except IntegrityError:
        logger.error(f'----------- error adding a new product => {traceback.format_exc()}')
        raise OmniException(message='Error adding a new product')


@transaction.atomic()
def update_product_in_stock(product_code: str, **kwargs: Dict[str, str]) -> Product:
    """
    Update a product inside db
    :param product_code: Product ID
    :param kwargs: Product information
    :return: Product updated
    """
    try:
        stock = Stock.objects.get(product__code=product_code)
        stock.product.name = kwargs['name'].strip()
        stock.product.price = kwargs['price']
        stock.product.category = kwargs['category']
        stock.units = kwargs['units']
        stock.product.description = kwargs['description']
        stock.product.save(update_fields=['name', 'price', 'description', 'category'])
        stock.save(update_fields=['units'])
        return stock.product
    except Stock.DoesNotExist:
        logger.error(f'----------- error updating a product => {traceback.format_exc()}')
        raise OmniException(message=f'Error updating a product. Product code {product_code} does not exist')


@transaction.atomic()
def delete_product_in_stock(product_code: str) -> None:
    """
    Delete a product inside db
    :param product_code: Product Code
    :return: None
    """
    try:
        Product.objects.get(code=product_code).delete()
    except Product.DoesNotExist:
        logger.error(f'----------- error removing a product => {traceback.format_exc()}')
        raise OmniException(message=f'Error removing a product. Product code {product_code} does not exist')


@transaction.atomic()
def add_order(products: List[Dict[str, str]]) -> Order:
    """
    Create a order subtracting units from Stock
    :param products: Product list
    :return: Order created
    """
    try:
        stocks = Stock.objects.filter(product__code__in=[p['code'] for p in products])
        order = Order()
        if stocks.count() != len(products):
            raise OmniException(message='Some product codes does not exist')
        order_total = 0.0  # order total (sum(product.price))
        order_items = []  # items to add in the order
        for stock in stocks:
            units_to_substract = [p['units'] for p in products if p['code'] == stock.product.code]
            # we have a valid value
            if units_to_substract:
                if stock.have_enough_units(int(units_to_substract[0])):
                    stock.units -= int(units_to_substract[0])
                    order_items.append(OrderDetail(product=stock.product, units=int(units_to_substract[0]),
                                                   order=order, price=stock.product.price))
                    order_total += int(units_to_substract[0]) * stock.product.price  # update order total
                else:
                    raise OmniException(message=f'Product with code {stock.product.code} does not have enough stock')
            else:
                raise OmniException(message='Some product does not have stock units configured')
        order.total = order_total
        order.save()
        OrderDetail.objects.bulk_create(order_items)
        Stock.objects.bulk_update(stocks, ['units'])  # update all products stock units
        return order
    except IntegrityError:
        logger.error(f'----------- error creating a order => {traceback.format_exc()}')
        raise OmniException(message=f'Error creating a order.')


@transaction.atomic()
def add_payment(orders: List[Dict[str, str]], payment_value: float) -> Payment:
    """
    Make a payment to one or more orders
    :param orders: Order list
    :param payment_value: Payment value
    :return: Payment created
    """
    try:
        _validate_payment_amount(orders, payment_value)  # payment value verification
        order_items = Order.objects.filter(code__in=[o['code'] for o in orders],
                                           state=OrderStateEnum.OUTSTANDING.value)
        if order_items.count() != len(orders):
            raise OmniException(message='Some order codes do not exist or have already been paid')
        payment = Payment(total=payment_value)  # Payment object
        payment_details = []  # payment details to add
        for item in order_items:
            payment_detail = PaymentDetail(order=item, payment=payment)
            if item.total == float(payment_value):
                payment_detail.amount = item.total
                item.total = 0
                item.state = OrderStateEnum.PAID.value
                payment_details.append(payment_detail)
                break
            elif item.total < float(payment_value):
                payment_detail.amount = item.total
                payment_value -= item.total
                item.total = 0
                item.state = OrderStateEnum.PAID.value
                payment_details.append(payment_detail)
            else:
                payment_detail.amount = payment_value
                item.total -= payment_value
                payment_details.append(payment_detail)
                break
        payment.save()
        Order.objects.bulk_update(order_items, ['total', 'state'])
        PaymentDetail.objects.bulk_create(payment_details)
    except IntegrityError:
        logger.error(f'----------- error creating a payment => {traceback.format_exc()}')
        raise OmniException(message=f'Error creating a payment.')
    except Exception as ex:
        logger.error(f'----------- Generic error creating a payment => {traceback.format_exc()}')
        if isinstance(ex, OmniException):
            raise
        raise OmniException(message='Generic error')


def _validate_payment_amount(orders: List[Dict[str, Any]], payment_value: float) -> None:
    """
    Make a payment validation.
    :param orders: Orders list
    :param payment_value: Payment value
    :return: None
    """
    total_orders = sum([order.total for order in Order.objects.filter(code__in=[o['code'] for o in orders])])
    if payment_value > total_orders:
        raise OmniException(message='Payment value is bigger than orders amounts')


@transaction.atomic()
def add_shipment(**kwargs: Dict[str, str]) -> Shipment:
    """
    Add a shipment inside db
    :param kwargs: Shipment information
    :return: Shipment added
    """
    try:
        order = Order.objects.get(code=kwargs['order'].strip())
        shipment = Shipment.objects.create(order=order, start_address=kwargs['start_address'].strip(),
                                           end_address=kwargs['end_address'].strip())
        return shipment
    except Order.DoesNotExist:
        logger.error(f'----------- error adding a new shipment => {traceback.format_exc()}')
        raise OmniException(message=f'Error adding a new shipment. Order with code {kwargs["order"]} does not exist')
    except IntegrityError:
        logger.error(f'----------- error adding a new shipment => {traceback.format_exc()}')
        raise OmniException(message='Error adding a new Shipment')
