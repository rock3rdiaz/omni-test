import logging

from rest_framework import viewsets

from api.mixins import ResponseMixin
from api.serializers import ProductSerializer, ProductModelSerializer
from ecomerce.domain import add_product_in_stock, OmniException, update_product_in_stock, delete_product_in_stock
from ecomerce.models import Product


logger = logging.getLogger(__name__)


class ProductViewset(viewsets.ViewSet, ResponseMixin):
    """
    Products application endpoints
    """
    def list(self, request):
        try:
            shipments = Product.objects.all()
            serializer = ProductModelSerializer(shipments, many=True)
            data = {
                'products': serializer.data
            }
            return self.build_ok('Product list', **data)
        except KeyError as ex:
            logger.error(f'---------------------------- {ex.args}')
            return self.build_bad_request('Invalid input, please check the documentation.')
        except OmniException as ex:
            return self.build_error(ex.message)

    def create(self, request):
        try:
            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                add_product_in_stock(code=request.data['code'],
                                     name=request.data['name'], category=request.data['category'],
                                     price=request.data['price'], units=request.data['units'],
                                     description=request.data.get('description', None))
                return self.build_ok('Product added successfully')
        except KeyError:
            return self.build_bad_request('Invalid input, please check the documentation.')
        except OmniException as ex:
            return self.build_error(ex.message)

    def update(self, request, pk=None):
        try:
            with_code = {'code': str(pk)}
            initial_data = {**request.data, **with_code}
            serializer = ProductSerializer(data=initial_data)
            if serializer.is_valid(raise_exception=True):
                update_product_in_stock(pk, name=request.data['name'], category=request.data['category'],
                                        price=request.data['price'], units=request.data['units'],
                                        description=request.data.get('description', None))
                return self.build_ok('Product updated successfully')
        except KeyError:
            return self.build_bad_request('Invalid input, please check the documentation.')
        except OmniException as ex:
            return self.build_error(ex.message)

    def destroy(self, request, pk=None):
        try:
            delete_product_in_stock(pk)
            return self.build_ok('Product removed successfully')
        except OmniException as ex:
            return self.build_error(ex.message)
