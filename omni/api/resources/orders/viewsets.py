import logging

from rest_framework import viewsets

from api.mixins import ResponseMixin
from api.serializers import OrderSerializer, OrderModelSerializer
from ecomerce.domain import OmniException, add_order
from ecomerce.models import Order

logger = logging.getLogger(__name__)


class OrderViewset(viewsets.ViewSet, ResponseMixin):
    """
    Orders application endpoints
    """
    def list(self, request):
        try:
            shipments = Order.objects.all()
            serializer = OrderModelSerializer(shipments, many=True)
            data = {
                'orders': serializer.data
            }
            return self.build_ok('Order list', **data)
        except KeyError as ex:
            logger.error(f'---------------------------- {ex.args}')
            return self.build_bad_request('Invalid input, please check the documentation.')
        except OmniException as ex:
            return self.build_error(ex.message)

    def create(self, request):
        try:
            serializer = OrderSerializer(data=request.data['products'], many=True)
            if serializer.is_valid(raise_exception=True):
                add_order(request.data['products'])
                return self.build_ok('Order added successfully')
        except KeyError:
            return self.build_bad_request('Invalid input, please check the documentation.')
        except OmniException as ex:
            return self.build_error(ex.message)