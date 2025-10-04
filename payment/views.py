from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework import status

from django.conf import settings
from cart_checkout.models import Order, CartItem, Cart
from .models import PaymentTransaction, Refund
from .serializers import PaymentTransactionSerializer, RefundSerializer

try:
    from sslcommerz_lib import SSLCOMMERZ
except Exception:
    SSLCOMMERZ = None


# ---------------- Checkout ----------------
class CheckoutAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Reuse cart from cart_checkout
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)

        if cart.items.count() == 0:
            return Response({"detail": "Cart is empty."}, status=400)

        from cart_checkout.serializers import CheckoutSerializer, OrderSerializer
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        total = cart.total_price()
        snapshot = [
            {
                "food_id": it.food.id,
                "name": it.food.name,
                "qty": it.quantity,
                "price": float(it.food.price),
            }
            for it in cart.items.select_related("food")
        ]

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            cart_snapshot=snapshot,
            delivery_address=data["delivery_address"],
            phone=data["phone"],
            total=total,
            payment_method=data["payment_method"],
            status="pending",
        )

        # COD: mark pending, clear cart
        if data["payment_method"] == "cod":
            cart.items.all().delete()
            return Response(OrderSerializer(order).data)

        # SSLCommerz
        if SSLCOMMERZ is None:
            return Response({"detail": "SSLCommerz library missing."}, status=500)

        settings_map = {
            "store_id": settings.SSL_COMMERZ_STORE_ID,
            "store_pass": settings.SSL_COMMERZ_STORE_PASSWORD,
            "issandbox": getattr(settings, "SSL_COMMERZ_SANDBOX", True),
        }
        sslcz = SSLCOMMERZ(settings_map)

        post_data = {
            "total_amount": float(total),
            "currency": "BDT",
            "tran_id": f"ORDER-{order.id}-{int(timezone.now().timestamp())}",
            "success_url": settings.SSL_COMMERZ_SUCCESS_URL,
            "fail_url": settings.SSL_COMMERZ_FAIL_URL,
            "cancel_url": settings.SSL_COMMERZ_CANCEL_URL,
            "ipn_url": settings.SSL_COMMERZ_IPN_URL,
            "cus_name": request.user.get_full_name() if request.user.is_authenticated else "Guest",
            "cus_email": getattr(request.user, "email", "guest@example.com"),
            "cus_add1": data["delivery_address"],
            "cus_phone": data["phone"],
        }
        response = sslcz.createSession(post_data)

        PaymentTransaction.objects.create(
            order=order,
            amount=total,
            raw_response=response,
            transaction_id=response.get("tran_id"),
        )

        return Response({
            "order": OrderSerializer(order).data,
            "payment_url": response.get("GatewayPageURL"),
        })


# ---------------- SSLCommerz IPN ----------------
@api_view(["POST"])
@permission_classes([AllowAny])
def sslcommerz_ipn(request):
    data = request.data
    tran_id = data.get("tran_id")
    status_val = data.get("status")

    import re
    m = re.search(r"ORDER-(\\d+)-", tran_id or "")
    if not m:
        return Response({"detail": "Invalid transaction ID"}, status=400)

    order_id = int(m.group(1))
    order = get_object_or_404(Order, id=order_id)

    PaymentTransaction.objects.create(
        order=order,
        amount=order.total,
        raw_response=data,
        transaction_id=data.get("val_id"),
        is_success=status_val in ("VALID", "SUCCESS", "Completed"),
    )

    if status_val in ("VALID", "SUCCESS", "Completed"):
        order.status = "paid"
        order.save()
        # clear cart
        CartItem.objects.filter(cart__user=order.user).delete()

    return Response({"ok": True})


# ---------------- SSLCommerz Redirect ----------------
@api_view(["GET"])
@permission_classes([AllowAny])
def sslcommerz_success(request):
    return Response({"detail": "Payment success. Awaiting IPN confirmation."})


# ---------------- Refund ----------------
@api_view(["POST"])
@permission_classes([IsAdminUser])
def request_refund(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    amount = float(request.data.get("amount", order.total))
    reason = request.data.get("reason", "")

    refund = Refund.objects.create(order=order, refund_amount=amount, reason=reason)

    if SSLCOMMERZ is None:
        refund.status = "failed"
        refund.raw_response = {"detail": "SSLCommerz library missing"}
        refund.save()
        return Response({"detail": "SSLCommerz library missing"}, status=500)

    settings_map = {
        "store_id": settings.SSL_COMMERZ_STORE_ID,
        "store_pass": settings.SSL_COMMERZ_STORE_PASSWORD,
        "issandbox": getattr(settings, "SSL_COMMERZ_SANDBOX", True),
    }
    sslcz = SSLCOMMERZ(settings_map)
    payload = {
        "merchant_trans_id": f"ORDER-{order.id}",
        "refund_amount": amount,
        "refund_remarks": reason,
        "refund_reference": f"REF-{order.id}-{int(timezone.now().timestamp())}",
    }

    try:
        resp = sslcz.initiate_refund(payload)
    except Exception as e:
        resp = {"error": str(e)}

    refund.raw_response = resp
    refund.refund_ref_id = resp.get("refund_ref_id") or payload["refund_reference"]
    refund.status = "processing" if resp and not resp.get("error") else "failed"
    refund.save()

    return Response(RefundSerializer(refund).data)

