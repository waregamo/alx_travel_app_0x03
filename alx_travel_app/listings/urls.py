from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ListingViewSet,
    BookingViewSet,
    welcome,
    initiate_payment,
    verify_payment
)

router = DefaultRouter()
router.register(r'listings', ListingViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('welcome/', welcome),
    path('payments/initiate/', initiate_payment, name='initiate_payment'),
    path('payments/verify/', verify_payment, name='verify_payment'),
]


