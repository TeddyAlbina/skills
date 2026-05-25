# Webhooks

## Overview

Webhooks deliver real-time HTTP POST notifications when events occur. Powered by [Svix](https://www.svix.com/).

**Supported events:** `payment_created`, `payment_status_updated`

## Create a Webhook

```bash
curl -X POST https://api.inflowpay.xyz/api/webhook \
  -H "X-Inflow-Api-Key: inflow_prod_your_key" \
  -H "Content-Type: application/json" \
  -d '{ "url": "https://yourserver.com/webhooks/inflow" }'
```

### Response

```json
{
  "webhookId": "webhook_abc123",
  "webhookUrl": "https://yourserver.com/webhooks/inflow",
  "secret": "whsec_your_webhook_secret"
}
```

> **Save the `secret`!** Only returned at creation. Required for signature verification.

## Limits

- Max **5 webhook endpoints** per account
- URLs must use **HTTPS** (HTTP not accepted)
- Inflow validates URL with HEAD request on creation

## Delivery & Retries

- Timeout: **15 seconds** for 2xx response
- Retries: **Exponential backoff**, up to **10 attempts** over hours/days
- Auto-disable: Endpoint disabled after exhausting retries
- Re-enable: Use update status endpoint after fixing issues

## Endpoint Requirements

- Accept HTTP `POST` requests
- Use HTTPS
- Return 2xx within 15 seconds
- Parse JSON body

---

## Event Types

| Event Type | When It Fires |
|---|---|
| `payment_created` | New payment created (checkout initiated) |
| `payment_status_updated` | Payment status changes |

## Payload Format

```json
{
  "data": [
    {
      "eventType": "payment_created",
      "payload": {
        "id": "pay_abc123",
        "amountInCents": 4999,
        "currency": "EUR",
        "status": "INITIATION",
        "customerEmail": "customer@example.com",
        "customerId": null,
        "products": [{ "name": "Product", "price": 4999, "quantity": 1 }],
        "metadatas": { "orderId": "order_12345" },
        "subscriptionId": null,
        "taxCountry": null,
        "amountTaxesIncluded": null,
        "depositStatus": null,
        "lastDepositAttempt": null,
        "taxRateInPercentage": null,
        "timeline": [
          { "status": "INITIATION", "timestamp": "2025-01-15T10:30:00.000Z" }
        ],
        "depositAttempts": [],
        "transactionSummary": null,
        "createdAt": "2025-01-15T10:30:00.000Z",
        "updatedAt": "2025-01-15T10:30:00.000Z"
      }
    }
  ]
}
```

> The `payload` is identical to the `GET /api/payment/{id}` response. No additional API call needed.

---

## Payment Statuses

| Status | Description |
|---|---|
| `INITIATION` | Payment created, waiting for payer |
| `CHECKOUT_PENDING` | Payer preparing payment |
| `CHECKOUT_SUCCESS` | Payer has paid |
| `PAYMENT_RECEIVED` | Funds received by banking provider |
| `PAYMENT_SUCCESS` | Funds in merchant account |
| `PAYMENT_FAILED` | Payment failed |
| `PARTIAL_REFUNDED` | Partial refund completed |
| `FULLY_REFUNDED` | Full refund completed |
| `REFUND_PENDING` | Refund processing |
| `REFUND_FAILED` | Refund failed |

---

## Subscription Payments

Subscription-related payments include `subscriptionId`:

```json
{
  "eventType": "payment_status_updated",
  "payload": {
    "id": "pay_sub_001",
    "status": "PAYMENT_SUCCESS",
    "subscriptionId": "sub_xyz789",
    "amountInCents": 2999,
    "currency": "EUR"
  }
}
```

---

## Payment Failure Detection

Check `lastDepositAttempt` for error details:

```json
{
  "lastDepositAttempt": {
    "status": "failed",
    "amount": 4999,
    "paymentMethod": "CARD",
    "error": "card_declined",
    "attemptedAt": "2025-01-15T10:31:00.000Z"
  }
}
```

---

## Manage Webhooks

```bash
# List all
curl https://api.inflowpay.xyz/api/webhook \
  -H "X-Inflow-Api-Key: inflow_prod_your_key"

# Get by ID
curl https://api.inflowpay.xyz/api/webhook/{webhookId} \
  -H "X-Inflow-Api-Key: inflow_prod_your_key"

# Get status
curl https://api.inflowpay.xyz/api/webhook/{webhookId}/status \
  -H "X-Inflow-Api-Key: inflow_prod_your_key"

# Update status (enable/disable)
curl -X PATCH https://api.inflowpay.xyz/api/webhook/{webhookId}/status \
  -H "X-Inflow-Api-Key: inflow_prod_your_key" \
  -H "Content-Type: application/json" \
  -d '{ "enabled": true }'

# Delete
curl -X DELETE https://api.inflowpay.xyz/api/webhook/{webhookId} \
  -H "X-Inflow-Api-Key: inflow_prod_your_key"
```

---

## Example Server (Node.js / Express)

```javascript
const express = require('express');
const app = express();

app.post('/webhooks/inflow', express.json(), (req, res) => {
  const { data } = req.body;

  for (const event of data) {
    const { eventType, payload } = event;

    switch (eventType) {
      case 'payment_created':
        console.log('New payment:', payload.id);
        break;
      case 'payment_status_updated':
        console.log(`Payment ${payload.id} → ${payload.status}`);
        break;
    }
  }

  res.status(200).json({ received: true });
});

app.listen(3000);
```

---

## Best Practices

- Return 2xx quickly — process events asynchronously if needed
- Use webhooks instead of polling for payment status
- Implement idempotency (events may be delivered more than once)
- Verify webhook signatures using the `secret`
- Monitor webhook health via the status endpoint
- Keep retry logic in mind — your endpoint must be resilient
