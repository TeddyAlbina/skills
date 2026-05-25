# Payments

## Payment Lifecycle

Every payment follows this status flow:

```
INITIATION → CHECKOUT_PENDING → CHECKOUT_SUCCESS → PAYMENT_RECEIVED → PAYMENT_SUCCESS
                                                                            ↓
                                                                     PAYMENT_FAILED
```

Additional statuses: `PARTIAL_REFUNDED`, `FULLY_REFUNDED`, `REFUND_PENDING`, `REFUND_FAILED`

## Integration Approaches

| Approach | Best For |
|---|---|
| **Payment Links** | Simple integration, no frontend work |
| **Checkout Redirect** | Programmatic creation, redirect to hosted checkout |
| **SDK (iframe)** | Custom checkout with PCI compliance handled |
| **Server-to-Server** | Full control, custom UI, PCI-compliant infrastructure |

---

## Payment Links

### Create via API

```bash
curl -X POST https://api.inflowpay.xyz/api/link \
  -H "X-Inflow-Api-Key: inflow_prod_your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "currency": "EUR",
    "products": [{ "name": "Product", "price": 2500, "quantity": 1 }]
  }'
```

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `currency` | string | Yes | `EUR` or `USD` |
| `products` | array | Yes | `name` (string), `price` (cents), `quantity` (number) |
| `status` | string | No | `enabled` (default) or `disabled` |
| `sessionCustomization` | object | No | `bgColor`, `fontColor`, `logoUrl`, `merchantName` |
| `pricingMode` | string | No | `TAX_EXCLUSIVE` (default) or `TAX_INCLUSIVE` |

### Link URL Format

```
https://checkout.inflowpay.com/l/{linkId}
```

### Manage Links

- **Archive:** `DELETE /api/link/{linkId}`
- **Unarchive:** `POST /api/link/{linkId}/unarchive`
- **Update:** `PATCH /api/link/{linkId}`
- **List:** `GET /api/link`
- **Get by ID:** `GET /api/link/{linkId}`

---

## Checkout Redirect

Create a payment and redirect the customer to the hosted checkout.

### Step 1: Create Payment

```bash
curl -X POST https://api.inflowpay.xyz/api/checkout/payment \
  -H "X-Inflow-Api-Key: inflow_prod_your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "products": [{ "name": "My Product", "price": 2999, "quantity": 1 }],
    "currency": "EUR",
    "customerEmail": "customer@example.com",
    "successUrl": "https://yoursite.com/success",
    "cancelUrl": "https://yoursite.com/cancel"
  }'
```

### Step 2: Redirect

Response includes `purchaseUrl` — redirect the customer there:

```json
{
  "paymentId": "pay_abc123",
  "purchaseUrl": "https://checkout.inflowpay.com/pay/pay_abc123"
}
```

### Step 3: Customer Completes Payment

After payment, customer is redirected to your `successUrl`.

---

## Server-to-Server Payments

> **Requires account activation.** Contact support@inflowpay.com to enable S2S.

> **Card data must go to `https://api-card.inflowpay.com`** (not the standard API URL).

### Step 1: Create Payment

```bash
curl -X POST https://api-card.inflowpay.com/api/server/payment \
  -H "X-Inflow-Api-Key: inflow_prod_your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "products": [{ "name": "Pro Plan", "price": 4999, "quantity": 1 }],
    "currency": "EUR",
    "customerEmail": "customer@example.com",
    "billingCountry": "FR",
    "postalCode": "75001",
    "purchasingAsBusiness": false,
    "firstName": "John",
    "lastName": "Doe",
    "autoConfirm": true,
    "pricingMode": "TAX_EXCLUSIVE",
    "threeDsSuccessUrl": "https://yoursite.com/3ds-success",
    "threeDsFailureUrl": "https://yoursite.com/3ds-failure",
    "metadatas": { "orderId": "order_12345" }
  }'
```

### S2S Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `products` | array | Yes | `name`, `price` (cents), `quantity` |
| `currency` | string | Yes | `EUR` or `USD` |
| `customerEmail` | string | Yes | Customer email |
| `billingCountry` | string | Yes | ISO 3166-1 alpha-2 code (e.g., `FR`, `DE`, `US`) |
| `purchasingAsBusiness` | boolean | Yes | Business purchase flag |
| `postalCode` | string | If US | Billing postal code |
| `businessName` | string | If business | Required if `purchasingAsBusiness: true` |
| `taxId` | string | If business | Required if `purchasingAsBusiness: true` |
| `firstName` | string | No | Recommended for 3DS success |
| `lastName` | string | No | Recommended for 3DS success |
| `savePaymentMethod` | boolean | No | Save card for future use |
| `useCustomerPaymentMethod` | boolean | No | Use last saved card (same email) |
| `autoConfirm` | boolean | No | Auto-confirm if no 3DS needed |
| `pricingMode` | string | No | `TAX_EXCLUSIVE` (default) or `TAX_INCLUSIVE` |
| `threeDsSuccessUrl` | string | No | Redirect after successful 3DS |
| `threeDsFailureUrl` | string | No | Redirect after failed 3DS |
| `metadatas` | object | No | Custom metadata |

### Step 2: Handle 3D Secure

If `threeDsSessionUrl` is not null in the response:

1. Redirect customer to `threeDsSessionUrl`
2. Customer completes bank authentication
3. Customer is redirected to `threeDsSuccessUrl` or `threeDsFailureUrl`

### Step 3: Confirm Payment

If `depositStatus` shows `"requires_confirmation"`:

```bash
curl -X POST https://api.inflowpay.xyz/api/server/payment/{paymentId}/confirm \
  -H "X-Inflow-Api-Key: inflow_prod_your_key"
```

> If `autoConfirm: true` and no 3DS required, confirmation is automatic.

### Step 4: Verify Status

```bash
curl https://api.inflowpay.xyz/api/payment/{paymentId} \
  -H "X-Inflow-Api-Key: inflow_prod_your_key"
```

Or use webhooks for automatic notifications.

### Update Payment Before Confirmation

```bash
curl -X PATCH https://api.inflowpay.xyz/api/server/payment/{paymentId} \
  -H "X-Inflow-Api-Key: inflow_prod_your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "products": [{ "name": "Updated Product", "price": 5999, "quantity": 1 }]
  }'
```

### Saving & Reusing Payment Methods

- **`savePaymentMethod: true`** — Saves card on first purchase (tied to `customerEmail`)
- **`useCustomerPaymentMethod: true`** — Uses last saved card for returning customer

Cannot use both in the same request. The last saved card is used automatically.

---

## Refunds

Refundable statuses: `CHECKOUT_SUCCESS`, `PAYMENT_RECEIVED`, `PAYMENT_SUCCESS`

### Via API

```bash
curl -X POST https://api.inflowpay.xyz/api/payment/{paymentId}/refund \
  -H "X-Inflow-Api-Key: inflow_prod_your_key" \
  -H "Content-Type: application/json" \
  -d '{ "reason": "Customer requested cancellation" }'
```

### Refund Statuses

| Status | Description |
|---|---|
| `REFUND_PENDING` | Processing |
| `FULLY_REFUNDED` | Full amount refunded |
| `PARTIAL_REFUNDED` | Partial refund |

> API currently supports **full refunds only**. Refunds deducted from your Inflow balance. Card refunds appear on statement within 5–10 business days.

---

## Tax & Pricing Modes

| Mode | Description |
|---|---|
| `TAX_EXCLUSIVE` | Tax added on top of product price (default) |
| `TAX_INCLUSIVE` | Tax included in product price |

Tax is calculated automatically based on `billingCountry`. Get tax rate via:

```bash
curl https://api.inflowpay.xyz/api/payment/tax-rate?country=FR \
  -H "X-Inflow-Api-Key: inflow_prod_your_key"
```

---

## Metadata

Attach custom JSON key-value data to payments for internal tracking:

```json
{
  "metadatas": {
    "orderId": "order_12345",
    "userId": "user_abc",
    "source": "mobile_app"
  }
}
```

Metadata is returned in payment details and webhook payloads.

---

## Get Payment Details

```bash
# By ID
curl https://api.inflowpay.xyz/api/payment/{paymentId} \
  -H "X-Inflow-Api-Key: inflow_prod_your_key"

# List all (paginated)
curl https://api.inflowpay.xyz/api/payment?page=1&limit=20 \
  -H "X-Inflow-Api-Key: inflow_prod_your_key"
```
