# ALX Travel App 0x02 – Chapa Payment Integration

## Objective
Integrate the **Chapa API** for handling secure online payments in a Django-based travel booking application.  
The integration enables users to make bookings and pay securely via Chapa, with payment status tracking and email confirmations.

---

## Features
- User-friendly API endpoints
- Swagger API documentation
- Payment integration using Chapa
- Redirect to Swagger UI on root access
- API versioning
---

## Tech Stack
- **Backend**: Django, Django REST Framework
- **API Documentation**: drf-yasg (Swagger UI)
- **Payment Gateway**: Chapa API
- **Database**: SQLite (Development) / PostgreSQL (Production)

---
## API Documentation
The API uses Swagger UI for documentation.

Swagger UI: http://127.0.0.1:8000/swagger/

---
## Payment Flow (Chapa)
Client sends a POST request to the payment endpoint with:

Amount

Currency

Email

First name and last name

Callback URL

Server sends payment data to Chapa API

Chapa returns a checkout_url and tx_ref

Client is redirected to the checkout page

Example Chapa Response:

{
    "checkout_url": "https://checkout.chapa.co/checkout/payment/HCqOk4C67u3f22LZDsLNeLYqfmcGLcTJ2IyMxxHcYuZqG",
    "tx_ref": "0329b24e-431f-4b9c-b161-f9fba9467762"
}
---

## Setup Instructions

### 1. Duplicate Project
Clone the existing `alx_travel_app_0x01` project into a new directory named `alx_travel_app_0x02`:
```bash
cp -r alx_travel_app_0x01 alx_travel_app_0x02
cd alx_travel_app_0x02






