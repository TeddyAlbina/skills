---
name: inflowpay
description: >
  Integrate InflowPay payment infrastructure — accept one-time payments (payment links, checkout redirect, embedded SDK, server-to-server), manage recurring subscriptions, handle webhooks, process refunds, set up marketplace Connect flows with sub-merchants, and manage payouts to bank accounts or crypto wallets. Use when building payment flows, checkout integrations, subscription billing, marketplace platforms, or any task involving the InflowPay API.
license: Proprietary
compatibility: Requires network access to api.inflowpay.xyz and api-card.inflowpay.com. SDK requires npm for @inflow_pay/sdk package.
metadata:
  author: inflowpay
  version: "2.0"
  documentation: https://docs.inflowpay.com
  api-reference: https://docs.inflowpay.com/reference
---

# InflowPay Agent Skill

Comprehensive guide for integrating InflowPay — a payment infrastructure platform for accepting global payments and managing payouts.

## Quick Start

**Base URLs:**
| Environment | URL | Use Case |
|---|---|---|
| Production | `https://api.inflowpay.xyz` | All API calls except S2S card data |
| Card Payments | `https://api-card.inflowpay.com` | Server-to-server card data transmission |

**Authentication:** All requests require `X-Inflow-Api-Key` header with your private key. Client-side SDK uses `X-Inflow-Public-Key`.

**Prices are in cents:** €25.00 = `2500`, $1.50 = `150`.

**Minimum amounts:** EUR: €1.50 (150 cents) | USD: $2.00 (200 cents)

See [Authentication & API Keys](references/authentication.md) for full details.

## Core Integration Paths

### 1. Payment Links (No Code)
Create shareable URLs from Dashboard or API. Customer is redirected to hosted checkout.

```bash
curl -X POST https://api.inflowpay.xyz/api/link \
  -H "X-Inflow-Api-Key: inflow_prod_your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "currency": "EUR",
    "products": [{ "name": "Product", "price": 2500, "quantity": 1 }]
  }'
```

See [Payments](references/payments.md) for checkout redirect, server-to-server, and all payment flows.

### 2. SDK (Embedded Card Form)
Embed a PCI-compliant card form on your site via iframe. Supports React and vanilla JS.

```bash
npm install @inflow_pay/sdk
```

See [SDK Integration](references/sdk.md) for React, vanilla JS, styling, and 3DS handling.

### 3. Server-to-Server (Full Control)
Process card details directly through your backend. Requires account activation.

**Important:** Send card data to `https://api-card.inflowpay.com`, not the standard API URL.

See [Payments](references/payments.md#server-to-server-payments) for S2S flow details.

### 4. Subscriptions (Recurring Billing)
Create subscription offers with flexible intervals, trials, entry fees, and Discord integration.

```bash
curl -X POST https://api.inflowpay.xyz/subscription/offer \
  -H "X-Inflow-Api-Key: your_private_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pro Plan",
    "amountInCents": 2999,
    "currency": "EUR",
    "interval": "month",
    "intervalCount": 1
  }'
```

See [Subscriptions](references/subscriptions.md) for offers, trials, waitlists, and management.

### 5. Connect (Marketplace)
Onboard sub-merchants, split payments, collect platform fees, route payouts.

See [Inflow Connect](references/connect.md) for marketplace flows and KYC/KYB.

## Payment Methods

| Method | Status | Region |
|---|---|---|
| Open Banking (SEPA, Faster Payments) | Live | EU / UK |
| Card Payments (Visa, Mastercard, Amex, Discover) | Live | Global |
| Apple Pay / Google Pay | Coming Soon | — |

## Key Resources

- **API Reference:** https://docs.inflowpay.com/reference
- **Dashboard:** https://dashboard.inflowpay.com
- **Support:** support@inflowpay.com

## Reference Files

| File | Contents |
|---|---|
| [Authentication](references/authentication.md) | API keys, headers, request format |
| [Payments](references/payments.md) | Checkout, S2S, payment links, refunds |
| [Subscriptions](references/subscriptions.md) | Offers, trials, management |
| [Webhooks](references/webhooks.md) | Setup, events, payloads, best practices |
| [SDK](references/sdk.md) | React, vanilla JS, styling, 3DS |
| [Connect](references/connect.md) | Marketplace, sub-merchants, KYC, fees |
| [Payouts](references/payouts.md) | Bank accounts, crypto wallets, balance |
| [Errors](references/errors.md) | Error codes, handling strategies |
| [Testing](references/testing.md) | Sandbox, test cards, 3DS scenarios |

## Workflow Guide

**"I want to accept a one-time payment"**
→ Use payment links (Dashboard or API) or SDK card form.
→ See [Payments](references/payments.md)

**"I want recurring billing"**
→ Create a subscription offer, share the link.
→ See [Subscriptions](references/subscriptions.md)

**"I want to build a marketplace"**
→ Use Connect to onboard sub-merchants and split payments.
→ See [Connect](references/connect.md)

**"I want to embed a checkout on my site"**
→ Use the @inflow_pay/sdk package.
→ See [SDK](references/sdk.md)

**"I want real-time payment notifications"**
→ Set up webhooks for payment_created and payment_status_updated events.
→ See [Webhooks](references/webhooks.md)

**"I want to test my integration"**
→ Use sandbox environment and test card numbers.
→ See [Testing](references/testing.md)
