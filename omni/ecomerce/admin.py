from django.contrib import admin

from ecomerce.models import Product, Order, OrderDetail, Payment, PaymentDetail, Stock, Shipment

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderDetail)
admin.site.register(Payment)
admin.site.register(PaymentDetail)
admin.site.register(Stock)
admin.site.register(Shipment)

