from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.resources.products.viewsets import ProductViewset
from api.resources.orders.viewsets import OrderViewset
from api.resources.payments.viewsets import PaymentViewset
from api.resources.shipments.viewsets import ShipmentViewset

app_name = 'api'

router = DefaultRouter()
router.register(r'products', ProductViewset, basename='products')
router.register(r'orders', OrderViewset, basename='orders')
router.register(r'payments', PaymentViewset, basename='payments')
router.register(r'shipments', ShipmentViewset, basename='shipments')

urlpatterns = [
    path('', include(router.urls))
]