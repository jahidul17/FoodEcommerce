from rest_framework import serializers
from .models import PaymentTransaction, Refund

class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = "__all__"

class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = "__all__"
        read_only_fields = ("requested_at","refund_ref_id","status","raw_response")


