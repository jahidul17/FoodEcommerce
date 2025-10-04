from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem, Order
from .serializers import CartSerializer, CartItemSerializer, CheckoutSerializer, OrderSerializer

class CartViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def _get_cart(self, request):
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
        return cart

    def list(self, request):
        cart = self._get_cart(request)
        return Response(CartSerializer(cart).data)

    @action(methods=["post"], detail=False)
    def add(self, request):
        cart = self._get_cart(request)
        from menu.models import FoodItem
        food = get_object_or_404(FoodItem, id=request.data.get("food"))
        qty = int(request.data.get("quantity", 1))
        item, created = CartItem.objects.get_or_create(cart=cart, food=food, defaults={"quantity": qty})
        if not created:
            item.quantity += qty
            item.save()
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)

    @action(methods=["post"], detail=False)
    def update_quantity(self, request):
        cart = self._get_cart(request)
        item = get_object_or_404(CartItem, id=request.data.get("item_id"), cart=cart)
        qty = int(request.data.get("quantity", 1))
        if qty <= 0:
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        item.quantity = qty
        item.save()
        return Response(CartItemSerializer(item).data)

    @action(methods=["post"], detail=False)
    def remove(self, request):
        cart = self._get_cart(request)
        item = get_object_or_404(CartItem, id=request.data.get("item_id"), cart=cart)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


