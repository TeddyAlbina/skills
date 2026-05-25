# Testing

## Sandbox Environment

Inflow provides a dedicated sandbox for testing without real funds.

> **Sandbox and production are fully isolated.** Mixing keys and base URLs returns `401 Unauthorized`.

**Sandbox base URL:** Check dashboard or contact support for sandbox URL.

**Sandbox API keys:** Generated separately from sandbox dashboard.

---

## Test Cards

Use any future expiry date (e.g., `12/2034`) and any valid CVC (3 digits for Visa/MC/Discover/UnionPay, 4 digits for Amex).

> **Only use test cards in sandbox.** These numbers are rejected in production. Never use real card numbers in sandbox.

### Success & Decline Cards

Available on SDK and hosted Checkout.

| Card Number | Type | Brand | Description | Issuer Country |
|---|---|---|---|---|
| `4242424242424242` | Credit | Visa | Success | Bermuda |
| `5555555555554444` | Credit | Mastercard | Success | Türkiye |
| `378282246310005` | Credit | Amex | Success | Faroe Islands |
| `4000056655665556` | Debit | Visa | Success | Chile |
| `6200000000000005` | Credit | UnionPay | Success | Svalbard & Jan Mayen |
| `4000000000000002` | Credit | Visa | Generic decline | — |
| `4000000000009995` | Credit | Visa | Insufficient funds | — |

### 3DS Test Cards

SDK only.

| Card Number | Brand | 3DS Scenario |
|---|---|---|
| `5204247750001471` | Mastercard | Successful Frictionless |
| `6011601160116011` | Discover | Successful Frictionless |
| `340000000004001` | Amex | Successful Frictionless |
| `4000020000000000` | Visa | Successful Challenge |
| `370000000000002` | Amex | Successful Challenge |
| `4111111111111111` | Visa | Attempted — succeeds |
| `4264281511112228` | Visa | Failed — declined |
| `5424180000000171` | Mastercard | Failed — declined |

> Using unlisted card numbers may produce unexpected results.

---

## Testing Checklist

1. **Payment creation** — Verify checkout redirect or SDK form appears
2. **Successful payment** — Use success cards, check status reaches `PAYMENT_SUCCESS`
3. **Declined payment** — Use decline cards, verify error handling
4. **3DS flow** — Use 3DS cards, verify redirect and completion
5. **Webhooks** — Confirm `payment_created` and `payment_status_updated` events received
6. **Refunds** — Issue refund, verify status changes to `FULLY_REFUNDED`
7. **Subscriptions** — Create offer, initiate subscription, verify recurring charge
8. **Error handling** — Test with invalid data, verify error responses

---

## Minimum Amounts

| Currency | Minimum |
|---|---|
| EUR | €1.50 (150 cents) |
| USD | $2.00 (200 cents) |

---

## Tips

- Always use small test amounts in production testing
- Check both API responses and webhook payloads
- Test 3DS flows thoroughly — they affect payment success rates
- Verify metadata appears in webhook payloads
- Test refund flow end-to-end
