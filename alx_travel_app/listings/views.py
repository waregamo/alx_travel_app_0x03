from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, status
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer
from .tasks import send_booking_email

import uuid
import requests
from django.conf import settings


@api_view(['GET'])
def welcome(request):
    return Response({"message": "Welcome to ALX Travel API!"})


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()

        # Trigger the email task asynchronously using customer_email
        user_email = booking.customer_email
        booking_details = f"Booking ID: {booking.id}, Customer: {booking.customer_name}, Check-in: {booking.check_in}, Check-out: {booking.check_out}, Listing: {booking.listing.title}"
        send_booking_email.delay(user_email, booking_details)

        return Response(serializer.data)


@api_view(['POST'])
def initiate_payment(request):
    booking_reference = request.data.get("booking_reference")
    amount = request.data.get("amount")

    if not booking_reference or not amount:
        return Response({"error": "booking_reference and amount are required"}, status=status.HTTP_400_BAD_REQUEST)

    tx_ref = str(uuid.uuid4())

    payment = Payment.objects.create(
        booking_reference=booking_reference,
        amount=amount,
        tx_ref=tx_ref,
        currency=settings.CHAPA_CURRENCY,
        status="PENDING"
    )

    chapa_url = f"{settings.CHAPA_BASE_URL}/v1/transaction/initialize"
    headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}
    data = {
        "amount": str(amount),
        "currency": settings.CHAPA_CURRENCY,
        "email": "waregamoses20@gmail.com",
        "first_name": "John",
        "last_name": "kelvin",
        "tx_ref": tx_ref,
        "callback_url": settings.CHAPA_CALLBACK_URL,
        "return_url": settings.CHAPA_RETURN_URL,
        "customization[title]": "Booking Payment",
        "customization[description]": f"Payment for booking {booking_reference}"
    }

    try:
        response = requests.post(chapa_url, headers=headers, json=data)
        resp_data = response.json()

        if resp_data.get("status") == "success":
            return Response({
                "checkout_url": resp_data["data"]["checkout_url"],
                "tx_ref": tx_ref
            })
        else:
            return Response(resp_data, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def verify_payment(request):
    tx_ref = request.query_params.get("tx_ref")
    if not tx_ref:
        return Response({"error": "tx_ref is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        payment = Payment.objects.get(tx_ref=tx_ref)
    except Payment.DoesNotExist:
        return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

    chapa_url = f"{settings.CHAPA_BASE_URL}/v1/transaction/verify/{tx_ref}"
    headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}

    try:
        response = requests.get(chapa_url, headers=headers)
        resp_data = response.json()

        if resp_data.get("status") == "success" and resp_data["data"]["status"] == "success":
            payment.status = "COMPLETED"
            payment.transaction_id = resp_data["data"]["transaction_id"]
            payment.save()
            return Response({"message": "Payment successful", "payment_status": payment.status})
        else:
            payment.status = "FAILED"
            payment.save()
            return Response({"message": "Payment failed", "payment_status": payment.status})

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
