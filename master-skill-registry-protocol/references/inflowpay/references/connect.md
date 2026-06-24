# Inflow Connect (Marketplace)

> Connect is currently in beta. Contact your Inflow contact to enable it.

## Overview

Inflow Connect enables marketplace platforms to onboard sub-merchants, accept payments on their behalf, take platform fees, and route payouts — all through a single API key.

**Model:** Marketplace holds one Inflow account. Each sub-merchant is a separate Inflow user with own KYC, balance, and payout destination. Marketplace acts on behalf of sub-merchants via `X-On-Behalf-Of` header.

## When to Use Connect

- Multi-seller platform (creators, marketplaces, SaaS)
- Need separate balances per seller
- Per-transaction platform fee auto-collected
- Sellers receive funds in stablecoins (USDC/EURC)

If you only accept payments for your own business, use the standard API.

## Key Concepts

| Concept | Description |
|---|---|
| **Marketplace** | Your Inflow account with Connect enabled |
| **Sub-merchant** | Separate Inflow user belonging to your marketplace |
| **Connect settings** | Per-marketplace config: fees, payout window, redirects |
| **`X-On-Behalf-Of`** | Header to act as a specific sub-merchant |
| **KYC / KYB** | Per-sub-merchant identity verification |
| **Marketplace fee** | Your take rate per transaction |

## Supported Currencies

| Stablecoin | Default | Configurable |
|---|---|---|
| USDC | Yes | `enabledCurrencies` in settings |
| EURC | Yes | `enabledCurrencies` in settings |

Fiat payments (card, SEPA, ACH) are converted to configured stablecoin on-rail.

---

## High-Level Flow

```
1. Marketplace creates sub-merchant (POST /api/connect/accounts)
2. Sub-merchant completes KYC via provided URL
3. Marketplace accepts payments on behalf of sub-merchant (X-On-Behalf-Of)
4. Funds split: sub-merchant (net) + marketplace fee + Inflow fees
5. Sub-merchant receives payout to bank/wallet
```

---

## Create Sub-merchant

```bash
curl -X POST https://api.inflowpay.xyz/api/connect/accounts \
  -H "X-Inflow-Api-Key: inflow_prod_your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seller@example.com",
    "type": "INDIVIDUAL",
    "firstName": "Jane",
    "lastName": "Smith"
  }'
```

Response includes `nextUrl` for KYC redirect.

## Get Sub-merchant

```bash
curl https://api.inflowpay.xyz/api/connect/accounts/{subMerchantId} \
  -H "X-Inflow-Api-Key: inflow_prod_your_key"
```

## List Sub-merchants

```bash
curl https://api.inflowpay.xyz/api/connect/accounts?page=1&limit=20 \
  -H "X-Inflow-Api-Key: inflow_prod_your_key"
```

## Update Sub-merchant Profile

```bash
curl -X PATCH https://api.inflowpay.xyz/api/connect/accounts/{subMerchantId} \
  -H "X-Inflow-Api-Key: inflow_prod_your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "displayName": "Jane'\''s Shop",
    "metadata": { "shopId": "shop_123" }
  }'
```

---

## KYC / KYB Flow

After creating a sub-merchant, the response includes `nextUrl` and `nextSteps`:

```json
{
  "id": "sub_abc123",
  "kycStatus": "PENDING",
  "nextUrl": "https://kyc.inflowpay.com/verify/sub_abc123",
  "nextSteps": ["redirect_user_to_next_url"]
}
```

### KYC Status Check

```bash
curl https://api.inflowpay.xyz/api/connect/accounts/{subMerchantId}/kyc \
  -H "X-Inflow-Api-Key: inflow_prod_your_key"
```

Returns current status and `nextUrl`/`nextSteps` for what to do next.

---

## Acting on Behalf Of

Use `X-On-Behalf-Of` header on standard merchant routes:

```bash
# Accept payment for sub-merchant
curl -X POST https://api.inflowpay.xyz/api/checkout/payment \
  -H "X-Inflow-Api-Key: inflow_prod_your_key" \
  -H "X-On-Behalf-Of: sub_abc123" \
  -H "Content-Type: application/json" \
  -d '{ ... }'

# Get sub-merchant balance
curl https://api.inflowpay.xyz/api/account/balance \
  -H "X-Inflow-Api-Key: inflow_prod_your_key" \
  -H "X-On-Behalf-Of: sub_abc123"

# Create payout for sub-merchant
curl -X POST https://api.inflowpay.xyz/api/account/payout \
  -H "X-Inflow-Api-Key: inflow_prod_your_key" \
  -H "X-On-Behalf-Of: sub_abc123" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

---

## Fees and Payouts

### Fee Math

On each payin:
1. Inflow fees deducted
2. Marketplace fee (your take rate) deducted
3. Remaining amount credited to sub-merchant

### Configure Fees

Via Connect settings or Dashboard.

### Payout Flow

Sub-merchants receive payouts to their configured bank account or crypto wallet.

---

## Suspension & Lifecycle

### Suspend Sub-merchant

```bash
curl -X POST https://api.inflowpay.xyz/api/connect/accounts/{subMerchantId}/suspend \
  -H "X-Inflow-Api-Key: inflow_prod_your_key"
```

Blocks `X-On-Behalf-Of` actions, pauses settlement. Idempotent.

### Resume Sub-merchant

```bash
curl -X POST https://api.inflowpay.xyz/api/connect/accounts/{subMerchantId}/resume \
  -H "X-Inflow-Api-Key: inflow_prod_your_key"
```

Clears suspension. Idempotent.

---

## Marketplace Settings

```bash
# Get settings
curl https://api.inflowpay.xyz/api/connect/settings \
  -H "X-Inflow-Api-Key: inflow_prod_your_key"

# Update settings
curl -X PATCH https://api.inflowpay.xyz/api/connect/settings \
  -H "X-Inflow-Api-Key: inflow_prod_your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "enabledCurrencies": ["USDC", "EURC"],
    "payoutWindow": "daily"
  }'
```

---

## Compliance

- Sub-merchants must complete KYC (individual) or KYB (business)
- Business activities must be in eligible categories
- Country restrictions apply for virtual IBANs
- See [Business Activities](#) and [Countries](#) for details
