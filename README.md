# E-Invoice Builder Supabase API

This is a FastAPI-based web API that uses Supabase as the backend database and authentication layer.

## Setup

1.  **Environment Variables**: The project uses a `.env` file for configuration. Ensure the following variables are set:
    *   `SUPABASE_URL`: Your Supabase Project URL.
    *   `SUPABASE_KEY`: Your Supabase Service Role Key or Anon Key (depending on RLS).
    *   `SECRET_KEY`: A secure key for JWT token generation.

2.  **Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Running the API**:
    ```bash
    uvicorn app.main:app --reload
    ```

## Supabase Tables

The following tables are expected to exist in your Supabase project:

*   `epay_users`: userId (int, pk), emailId (text, unique), fullName (text), phoneNumber (text), hashPassword (text), algoPassword (text), isActive (bool), createdOn (timestamp).
*   `epay_roles`: roleId (int, pk), roleName (text, unique).
*   `epay_user_roles`: userRoleId (int, pk), userId (int, fk), roleId (int, fk).
*   `epay_business_types`: businessTypeId (int, pk), businessTypeName (text, unique), isActive (bool).
*   `epay_business`: businessId (int, pk), businessName (text, unique), businessTypeId (int, fk), userId (int, fk), businessLogo (text), businessAddress (text), isActive (bool), templateStatus (text).
*   `epay_customers`: customerId (int, pk), businessId (int, fk), customerName (text), customerPhone (text), customerFullAddress (text).
*   `epay_invoices`: invoiceId (int, pk), businessId (int, fk), customerId (int, fk), invoiceNumber (text), invoiceAmount (int), amountInWords (text), paymentMode (text), paymentType (text), purpose (text), pdfURL (text).
*   `epay_subscription_plans`: subscriptionPlanId (int, pk), subscriptionPlanName (text), ...
*   `epay_subscriptions`: subscriptionId (int, pk), businessId (int, fk), subscriptionPlanId (int, fk), ...

## Authentication
The API uses custom JWT authentication. The `/auth/token` endpoint provides an access token which should be included in the `Authorization: Bearer <token>` header for protected routes.
