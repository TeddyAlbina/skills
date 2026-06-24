# Subscriptions

## Overview

Subscriptions enable recurring billing with flexible intervals, trials, entry fees, waitlists, and Discord role integration.

**Key concepts:**
- **Subscription Offer** — Template defining price, interval, and features
- **Subscription** — Active relationship between customer and offer
- **Subscription Link** — Auto-generated URL: `checkout.inflowpay.com/subscribe/{offerId}`

## Create a Subscription Offer

### Via API

```bash
curl -X POST https://api.inflowpay.xyz/subscription/offer \
  -H "X-Inflow-Api-Key: your_private_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pro Plan",
    "description": "Full access to all features",
    "amountInCents": 2999,
    "currency": "EUR",
    "interval": "month",
    "intervalCount": 1,
    "trialPeriodDays": 14,
    "waitlistEnabled": false,
    "pricingMode": "TAX_EXCLUSIVE",
    "successUrl": "https://yoursite.com/welcome",
    "cancelUrl": "https://yoursite.com/pricing",
    "sessionCustomization": {
      "bgColor": "#ffffff",
      "fontColor": "#000000",
      "logoUrl": "https://yoursite.com/logo.png",
      "merchantName": "Your Brand"
    }
  }'
```

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Offer name |
| `description` | string | Yes | Offer description |
| `amountInCents` | number | Yes | Price per cycle in cents (min 150, max 99999999) |
| `currency` | string | Yes | `EUR` or `USD` |
| `interval` | string | Yes | `day`, `week`, `month`, or `year` |
| `intervalCount` | number | Yes | Intervals between charges (e.g., 2 = every 2 months) |
| `trialPeriodDays` | number | No | Free trial days (1–365) |
| `entryFeesInCents` | number | No | First payment amount (min 150) |
| `cycleCount` | number | No | Total billing cycles (min 2, empty = unlimited) |
| `waitlistEnabled` | boolean | No | Require manual approval |
| `pricingMode` | string | No | `TAX_EXCLUSIVE` (default) or `TAX_INCLUSIVE` |
| `extraInfoNeeded` | boolean | No | Collect extra info at checkout |
| `discordGuildId` | string | No | Discord server ID |
| `discordRoleId` | string | No | Discord role ID to assign |
| `successUrl` | string | No | Redirect after successful subscription |
| `cancelUrl` | string | No | Redirect if customer cancels |
| `sessionCustomization` | object | No | Checkout appearance |

### Response

Returns the offer with its `id`. Subscription link:

```
https://checkout.inflowpay.com/subscribe/{offerId}
```

---

## Initiate Subscription (Checkout)

```bash
curl -X POST https://api.inflowpay.xyz/subscription/initiate \
  -H "X-Inflow-Api-Key: your_private_key" \
  -H "Content-Type: application/json" \
  -d '{
    "offerId": "offer_abc123",
    "customerEmail": "customer@example.com"
  }'
```

## Initiate Subscription (Server-to-Server)

```bash
curl -X POST https://api-card.inflowpay.com/subscription/initiate/server \
  -H "X-Inflow-Api-Key: your_private_key" \
  -H "Content-Type: application/json" \
  -d '{
    "offerId": "offer_abc123",
    "customerEmail": "customer@example.com",
    "billingCountry": "FR",
    "purchasingAsBusiness": false,
    "firstName": "John",
    "lastName": "Doe"
  }'
```

---

## Manage Subscriptions

### Cancel

```bash
curl -X POST https://api.inflowpay.xyz/subscription/{subscriptionId}/cancel \
  -H "X-Inflow-Api-Key: your_private_key"
```

### Reactivate (from PENDING_CANCELLATION)

```bash
curl -X POST https://api.inflowpay.xyz/subscription/{subscriptionId}/reactivate \
  -H "X-Inflow-Api-Key: your_private_key"
```

### Upgrade (prorated billing)

```bash
curl -X POST https://api.inflowpay.xyz/subscription/{subscriptionId}/upgrade \
  -H "X-Inflow-Api-Key: your_private_key" \
  -H "Content-Type: application/json" \
  -d '{ "newOfferId": "offer_xyz789" }'
```

### Get Subscription Details

```bash
curl https://api.inflowpay.xyz/subscription/{subscriptionId} \
  -H "X-Inflow-Api-Key: your_private_key"
```

### List Subscriptions

```bash
curl https://api.inflowpay.xyz/subscription?page=1&limit=20 \
  -H "X-Inflow-Api-Key: your_private_key"
```

### List Subscriptions by Offer

```bash
curl https://api.inflowpay.xyz/subscription/offer/{offerId}/subscriptions \
  -H "X-Inflow-Api-Key: your_private_key"
```

---

## Subscription Statuses

| Status | Description |
|---|---|
| `ACTIVE` | Subscription is active and billing |
| `PENDING_CANCELLATION` | Cancellation requested, active until period ends |
| `CANCELLED` | Subscription cancelled |
| `PAUSED` | Subscription paused |
| `PAST_DUE` | Payment failed, retry in progress |

---

## Advanced Features

### Trial Periods

Set `trialPeriodDays` (1–365) on the offer. Customer is not charged during trial.

### Entry Fees

Set `entryFeesInCents` for a different first payment amount. Minimum 150 cents.

### Waitlist

Set `waitlistEnabled: true`. Subscriptions require manual approval before activation.

### Cycle Limits

Set `cycleCount` to end subscription after N billing cycles (min 2).

### Discord Integration

Set `discordGuildId` and `discordRoleId` to automatically assign roles to active subscribers.

### Coupons

Apply coupons at checkout. See [Coupons](#coupons) section.

---

## Coupons

### Create a Coupon

```bash
curl -X POST https://api.inflowpay.xyz/api/coupon \
  -H "X-Inflow-Api-Key: your_private_key" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "SAVE20",
    "discountType": "percentage",
    "discountValue": 20,
    "maxRedemptions": 100
  }'
```

### Apply at Checkout

Coupons are applied by the customer during checkout on subscription links.

---

## Dashboard vs API

| Action | Dashboard | API |
|---|---|---|
| Create offer | Yes | Yes |
| List offers/subscriptions | Yes | Yes |
| Initiate subscription | Yes | Yes |
| Cancel subscription | Yes | Yes |
| Waitlist management | Yes | No |
| Archive/unarchive offers | Yes | No |
| Subscription metrics (MRR) | Yes | No |
