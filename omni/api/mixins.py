from typing import Dict

from rest_framework import status
from rest_framework.response import Response


class ResponseMixin:
    """
    Basic response wrapper
    """
    def _build(self, message: str, _status: int, **kwargs: Dict) -> Response:
        data = {
            'message': message
        }
        if kwargs:
            data['data'] = kwargs
        return Response(data=data, status=_status)

    def build_ok(self, message: str, **kwargs: Dict) -> Response:
        return self._build(message, status.HTTP_200_OK, **kwargs)

    def build_error(self, message: str) -> Response:
        return self._build(message, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def build_bad_request(self, message: str) -> Response:
        return self._build(message, status.HTTP_400_BAD_REQUEST)