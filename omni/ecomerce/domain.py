import traceback
from typing import Dict, List

from django.db import IntegrityError, transaction

from ecomerce.models import Product, Stock, Order


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
        print(f'----------- error adding a new product => {traceback.format_exc()}')
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
        print(f'----------- error updating a product => {traceback.format_exc()}')
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
        print(f'----------- error removing a product => {traceback.format_exc()}')
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
        if stocks.count() != len(products):
            raise OmniException(message='Some product codes does not exist')
        products_to_add = []  # products to add in order
        order_total = 0.0  # order total (sum(product.price))
        for stock in stocks:
            units_to_substract = [p['units'] for p in products if p['code'] == stock.product.code]
            # we have a valid value
            if units_to_substract:
                if stock.have_enough_units(int(units_to_substract[0])):
                    stock.units -= int(units_to_substract[0])
                    products_to_add.append(stock.product)
                    order_total += int(units_to_substract[0]) * stock.product.price  # update order total
                else:
                    raise OmniException(message=f'Product with code {stock.product.code} does not have enough stock')
            else:
                raise OmniException(message='Some product does not have stock units configured')
        order = Order.objects.create(total=order_total)
        order.products.add(*products_to_add)
        Stock.objects.bulk_update(stocks, ['units'])  # update all products stock units
        return order
    except IntegrityError:
        print(f'----------- error creating a order => {traceback.format_exc()}')
        raise OmniException(message=f'Error creating a order.')
