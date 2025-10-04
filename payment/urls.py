from django.urls import path
from .views import CheckoutAPIView, sslcommerz_ipn, sslcommerz_success, request_refund

urlpatterns = [
    path("checkout/", CheckoutAPIView.as_view(), name="checkout"),
    path("sslcommerz/ipn/", sslcommerz_ipn, name="sslcommerz-ipn"),
    path("sslcommerz/success/", sslcommerz_success, name="sslcommerz-success"),
    path("orders/<int:order_id>/refund/", request_refund, name="order-refund"),
]

