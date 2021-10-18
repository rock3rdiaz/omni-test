from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.resources.products.viewsets import ProductViewset
from api.resources.orders.viewsets import OrderViewset

app_name = 'api'

router = DefaultRouter()
router.register(r'products', ProductViewset, basename='products')
router.register(r'orders', OrderViewset, basename='orders')

urlpatterns = [
    path('', include(router.urls))
]