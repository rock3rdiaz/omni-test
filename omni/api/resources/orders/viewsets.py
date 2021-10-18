from rest_framework import viewsets

from api.mixins import ResponseMixin
from api.serializers import OrderSerializer
from ecomerce.domain import OmniException, add_order


class OrderViewset(viewsets.ViewSet, ResponseMixin):
    """
    Orders application endpoints
    """
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