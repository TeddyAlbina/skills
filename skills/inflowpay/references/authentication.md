# Authentication & API Keys

## Two Key Types

| Key | Header | Usage |
|---|---|---|
| **Private Key** (`inflow_prod_...`) | `X-Inflow-Api-Key` | Server-side only — payments, subscriptions, webhooks, refunds, customers, payouts. **Never expose to browser.** |
| **Public Key** (`inflow_pub_prod_...`) | `X-Inflow-Public-Key` | Client-side SDK only — iframe card form tokenization. Safe for frontend code. |

> **No sandbox yet.** Currently only production keys exist. A sandbox environment is on the roadmap.

## Required Headers

| Header | Required | Description |
|---|---|---|
| `Content-Type` | Yes (POST/PUT/PATCH) | Always `application/json` |
| `Accept` | Recommended | `application/json` |
| `X-Inflow-Api-Key` | Yes | Your private API key |

## Base URLs

| Environment | URL | Use Case |
|---|---|---|
| Production | `https://api.inflowpay.xyz` | All standard API calls |
| Card Payments | `https://api-card.inflowpay.com` | Server-to-server card data (PCI-compliant) |

## URL Prefixes by Resource

| Resource | Path Pattern |
|---|---|
| Payments | `https://api.inflowpay.xyz/api/payment` |
| Checkout payments | `https://api.inflowpay.xyz/api/checkout/payment` |
| Webhooks | `https://api.inflowpay.xyz/api/webhook` |
| Subscriptions | `https://api.inflowpay.xyz/subscription/...` (no `/api/` prefix) |
| Payment links | `https://api.inflowpay.xyz/api/link` |

## HTTP Methods

| Method | Usage |
|---|---|
| `GET` | Retrieve resources |
| `POST` | Create resources or perform actions |
| `PATCH` | Partially update a resource |
| `PUT` | Fully update a resource |
| `DELETE` | Delete or cancel |

## HTTP Status Codes

| Code | Meaning |
|---|---|
| `200` | Success (GET, PATCH, PUT, DELETE) |
| `201` | Created (POST) |
| `400` | Bad Request — invalid parameters |
| `401` | Unauthorized — invalid or missing API key |
| `404` | Not Found |
| `500` | Internal Server Error |

## Quick Example

```bash
curl -X POST https://api.inflowpay.xyz/api/checkout/payment \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "X-Inflow-Api-Key: inflow_prod_your_key" \
  -d '{
    "products": [{ "name": "Product", "price": 4999, "quantity": 1 }],
    "currency": "EUR",
    "customerEmail": "customer@example.com",
    "successUrl": "https://yoursite.com/success"
  }'
```

## Connect: Acting on Behalf of Sub-merchants

For marketplace flows, add the `X-On-Behalf-Of` header to target a specific sub-merchant:

```bash
curl -X POST https://api.inflowpay.xyz/api/checkout/payment \
  -H "X-Inflow-Api-Key: inflow_prod_your_key" \
  -H "X-On-Behalf-Of: sub_merchant_id" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

See [Connect](connect.md) for details.
