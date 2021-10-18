import logging

from rest_framework import viewsets

from api.mixins import ResponseMixin
from api.serializers import PaymentSerializer, PaymentModelSerializer
from ecomerce.domain import OmniException, add_payment
from ecomerce.models import Payment

logger = logging.getLogger(__name__)


class PaymentViewset(viewsets.ViewSet, ResponseMixin):
    """
    Payments application endpoints
    """
    def list(self, request):
        try:
            shipments = Payment.objects.all()
            serializer = PaymentModelSerializer(shipments, many=True)
            data = {
                'payments': serializer.data
            }
            return self.build_ok('Payment list', **data)
        except KeyError as ex:
            logger.error(f'---------------------------- {ex.args}')
            return self.build_bad_request('Invalid input, please check the documentation.')
        except OmniException as ex:
            return self.build_error(ex.message)

    def create(self, request):
        try:
            serializer = PaymentSerializer(data=request.data['orders'], many=True)
            if serializer.is_valid(raise_exception=True):
                add_payment(request.data['orders'], request.data['payment_amount'])
                return self.build_ok('Payment added successfully')
        except KeyError:
            return self.build_bad_request('Invalid input, please check the documentation.')
        except OmniException as ex:
            return self.build_error(ex.message)