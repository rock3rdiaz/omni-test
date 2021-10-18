import logging

from rest_framework import viewsets

from api.mixins import ResponseMixin
from api.serializers import ShipmentSerializer, ShipmentModelSerializer
from ecomerce.domain import OmniException, add_shipment
from ecomerce.models import Shipment


logger = logging.getLogger(__name__)


class ShipmentViewset(viewsets.ViewSet, ResponseMixin):
    """
    Shipment application endpoints
    """
    paginate_by = 2

    def list(self, request):
        try:
            shipments = Shipment.objects.all()
            serializer = ShipmentModelSerializer(shipments, many=True)
            data = {
                'shipments': serializer.data
            }
            return self.build_ok('Shipment added successfully', **data)
        except KeyError as ex:
            logger.error(f'---------------------------- {ex.args}')
            return self.build_bad_request('Invalid input, please check the documentation.')
        except OmniException as ex:
            return self.build_error(ex.message)

    def create(self, request):
        try:
            serializer = ShipmentSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                add_shipment(order=request.data['order'], start_address=request.data['start_address'],
                             end_address=request.data['end_address'])
                return self.build_ok('Shipment added successfully')
        except KeyError as ex:
            logger.error(f'---------------------------- {ex.args}')
            return self.build_bad_request('Invalid input, please check the documentation.')
        except OmniException as ex:
            return self.build_error(ex.message)