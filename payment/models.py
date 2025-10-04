from django.db import models
from cart_checkout.models import Order

class PaymentTransaction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="transactions")
    transaction_id = models.CharField(max_length=128, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    raw_response = models.JSONField(blank=True, null=True)
    is_success = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="refunds")
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField(blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    refund_ref_id = models.CharField(max_length=128, blank=True, null=True)
    status = models.CharField(max_length=32, default="requested")
    raw_response = models.JSONField(blank=True, null=True)

