from django.test import TestCase

from .domain import add_order, OmniException, _validate_payment_amount, add_payment
from .enums import ProductCategoryEnum, OrderStateEnum
from .models import Product, Stock, Order, OrderDetail


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


class PaymentTest(TestCase):
    def setUp(self):
        print('---- testing payments domain ...')

    def test_payment_value(self):
        p1 = Product.objects.create(code='P1', name='Product1', description='Product 1 description',
                                    price=100.0, category=ProductCategoryEnum.ELECTRONIC.value)
        p2 = Product.objects.create(code='P2', name='Product2', description='Product 2 description',
                                    price=70.0, category=ProductCategoryEnum.ELECTRONIC.value)
        p3 = Product.objects.create(code='P3', name='Product3', description='Product 3 description',
                                    price=20.0, category=ProductCategoryEnum.CLOTHING.value)
        Stock.objects.create(product=p1, units=10)
        Stock.objects.create(product=p2, units=20)
        Stock.objects.create(product=p3, units=20)
        order1 = Order.objects.create(total=270.0)
        OrderDetail.objects.create(order=order1, product=p1, units=2)
        OrderDetail.objects.create(order=order1, product=p2, units=1)
        order2 = Order.objects.create(total=100.0)
        OrderDetail.objects.create(order=order2, product=p3, units=5)
        with self.assertRaises(OmniException):
            data = {
                'orders': [
                    {
                        'code': str(order1.code)
                    },
                    {
                        'code': str(order2.code)
                    }
                ],
                'payment_amount': 1000.0
            }
            _validate_payment_amount(data['orders'], data['payment_amount'])

    def test_invalid_order_codes(self):
        p1 = Product.objects.create(code='P1', name='Product1', description='Product 1 description',
                                    price=100.0, category=ProductCategoryEnum.ELECTRONIC.value)
        p2 = Product.objects.create(code='P2', name='Product2', description='Product 2 description',
                                    price=70.0, category=ProductCategoryEnum.ELECTRONIC.value)
        p3 = Product.objects.create(code='P3', name='Product3', description='Product 3 description',
                                    price=20.0, category=ProductCategoryEnum.CLOTHING.value)
        Stock.objects.create(product=p1, units=10)
        Stock.objects.create(product=p2, units=20)
        Stock.objects.create(product=p3, units=20)
        order1 = Order.objects.create(total=270.0)
        OrderDetail.objects.create(order=order1, product=p1, units=2)
        OrderDetail.objects.create(order=order1, product=p2, units=1)
        order2 = Order.objects.create(total=100.0)
        OrderDetail.objects.create(order=order2, product=p3, units=5)
        with self.assertRaises(OmniException):
            data = {
                'orders': [
                    {
                        'code': 'd23d2179-5dce-4c31-9f5e-feae0e9f0cd8'  # fake code
                    },
                    {
                        'code': str(order2.code)
                    }
                ],
                'payment_amount': 40.0
            }
            add_payment(data['orders'], data['payment_amount'])

    def test_payments_value_eq_order_amounts(self):
        p1 = Product.objects.create(code='P1', name='Product1', description='Product 1 description',
                                    price=100.0, category=ProductCategoryEnum.ELECTRONIC.value)
        p2 = Product.objects.create(code='P2', name='Product2', description='Product 2 description',
                                    price=70.0, category=ProductCategoryEnum.ELECTRONIC.value)
        p3 = Product.objects.create(code='P3', name='Product3', description='Product 3 description',
                                    price=20.0, category=ProductCategoryEnum.CLOTHING.value)
        Stock.objects.create(product=p1, units=10)
        Stock.objects.create(product=p2, units=20)
        Stock.objects.create(product=p3, units=20)
        order1 = Order.objects.create(total=270.0)
        OrderDetail.objects.create(order=order1, product=p1, units=2, price=p1.price)
        OrderDetail.objects.create(order=order1, product=p2, units=1, price=p2.price)
        order2 = Order.objects.create(total=100.0)
        OrderDetail.objects.create(order=order2, product=p3, units=5, price=p3.price)
        data = {
            'orders': [
                {
                    'code': str(order1.code)
                },
                {
                    'code': str(order2.code)
                }
            ],
            'payment_amount': 370.0
        }
        add_payment(data['orders'], data['payment_amount'])
        self.assertEqual(sum([order.total for order in Order.objects.filter(code__in=[o['code'] for o in data['orders']])]),
                         0.0)

    def test_payments_value_lt_order_amounts(self):
        p1 = Product.objects.create(code='P1', name='Product1', description='Product 1 description',
                                    price=100.0, category=ProductCategoryEnum.ELECTRONIC.value)
        p2 = Product.objects.create(code='P2', name='Product2', description='Product 2 description',
                                    price=70.0, category=ProductCategoryEnum.ELECTRONIC.value)
        p3 = Product.objects.create(code='P3', name='Product3', description='Product 3 description',
                                    price=20.0, category=ProductCategoryEnum.CLOTHING.value)
        Stock.objects.create(product=p1, units=10)
        Stock.objects.create(product=p2, units=20)
        Stock.objects.create(product=p3, units=20)
        order1 = Order.objects.create(total=270.0)
        OrderDetail.objects.create(order=order1, product=p1, units=2, price=p1.price)
        OrderDetail.objects.create(order=order1, product=p2, units=1, price=p2.price)
        order2 = Order.objects.create(total=100.0)
        OrderDetail.objects.create(order=order2, product=p3, units=5, price=p3.price)
        data = {
            'orders': [
                {
                    'code': str(order1.code)
                },
                {
                    'code': str(order2.code)
                }
            ],
            'payment_amount': 300.0
        }
        add_payment(data['orders'], data['payment_amount'])
        o1 = Order.objects.get(code=order1.code)
        o2 = Order.objects.get(code=order2.code)
        self.assertEqual(o1.total, 0.0)  # check total
        self.assertEqual(o1.state, OrderStateEnum.PAID.value)  # check state
        self.assertEqual(o2.total, 70.0)  # check total
        self.assertEqual(o2.state, OrderStateEnum.OUTSTANDING.value)  # check state


class ShipmentTest(TestCase):
    def setUp(self):
        print('---- testing shipment domain ...')
