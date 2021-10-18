from django.test import TestCase

from .domain import add_order, OmniException
from .enums import ProductCategoryEnum
from .models import Product, Stock


class OrderTest(TestCase):
    def setUp(self):
        print('---- testing orders domain ...')

    def test_create_order(self):
        p1 = Product.objects.create(code='P1', name='Product1', description='Product 1 description',
                                    price=100.0, category=ProductCategoryEnum.ELECTRONIC.value)
        p2 = Product.objects.create(code='P2', name='Product2', description='Product 2 description',
                                    price=70.0, category=ProductCategoryEnum.ELECTRONIC.value)
        p3 = Product.objects.create(code='P3', name='Product3', description='Product 3 description',
                                    price=20.0, category=ProductCategoryEnum.CLOTHING.value)
        Stock.objects.create(product=p1, units=10)
        Stock.objects.create(product=p2, units=20)
        Stock.objects.create(product=p3, units=20)
        products = [
            {
                'code': 'P1',
                'units': 2
            },
            {
                'code': 'P2',
                'units': 4
            },
            {
                'code': 'P3',
                'units': 19
            }
        ]
        order = add_order(products)
        self.assertEqual(order.total, (2 * p1.price) + (4 * p2.price) + (19 * p3.price))  # check total order
        self.assertEqual(Stock.objects.get(product__code='P1').units, 8)  # check p1 stock units
        self.assertEqual(Stock.objects.get(product__code='P2').units, 16)  # check p2 stock units
        self.assertEqual(Stock.objects.get(product__code='P3').units, 1)  # check p3 stock units

    def test_enough_units(self):
        p1 = Product.objects.create(code='P1', name='Product1', description='Product 1 description',
                                    price=100.0, category=ProductCategoryEnum.ELECTRONIC.value)
        p2 = Product.objects.create(code='P2', name='Product2', description='Product 2 description',
                                    price=70.0, category=ProductCategoryEnum.ELECTRONIC.value)
        Stock.objects.create(product=p1, units=10)
        Stock.objects.create(product=p2, units=20)
        products = [
            {
                'code': 'P1',
                'units': 2
            },
            {
                'code': 'P2',
                'units': 100
            }
        ]
        with self.assertRaises(OmniException):
            add_order(products)
