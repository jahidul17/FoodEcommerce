from rest_framework import serializers
from .models import Cart, CartItem, Order

class CartItemSerializer(serializers.ModelSerializer):
    food_name = serializers.CharField(source="food.name", read_only=True)

    class Meta:
        model = CartItem
        fields = ("id", "food", "food_name", "quantity", "added_at")


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ("id", "user", "session_key", "items", "total")

    def get_total(self, obj):
        return obj.total_price()


class CheckoutSerializer(serializers.Serializer):
    delivery_address = serializers.CharField()
    phone = serializers.CharField()
    payment_method = serializers.ChoiceField(choices=[("sslcommerz","SSLCommerz"),("cod","Cash on Delivery")])


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


