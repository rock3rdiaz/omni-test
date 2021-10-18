from rest_framework import viewsets

from api.mixins import ResponseMixin
from api.serializers import PaymentSerializer
from ecomerce.domain import OmniException, add_payment


class PaymentViewset(viewsets.ViewSet, ResponseMixin):
    """
    Payments application endpoints
    """
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