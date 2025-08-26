from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_booking_email(user_email, booking_details):
    subject = 'Booking Confirmation'
    message = f"""Dear user,

Your booking has been confirmed. Details:
{booking_details}

Thank you for using ALX Travel App!"""
    from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(
        subject,
        message,
        from_email,
        [user_email],
        fail_silently=False,
    )
