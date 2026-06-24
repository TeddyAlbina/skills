# Error Handling

## API Error Format

All errors return consistent JSON:

```json
{
  "statusCode": 400,
  "message": "Validation failed",
  "error": "Bad Request"
}
```

Validation errors use array format:

```json
{
  "statusCode": 400,
  "message": [
    "currency must be one of the following values: EUR, USD",
    "customerEmail must be an email"
  ],
  "error": "Bad Request"
}
```

## HTTP Status Codes

| Code | Meaning | Action |
|---|---|---|
| `200` | Success | — |
| `201` | Created | — |
| `400` | Bad Request | Check request body |
| `401` | Unauthorized | Verify API key |
| `404` | Not Found | Resource doesn't exist |
| `500` | Internal Server Error | Retry with backoff |

---

## Payment Error Codes

Found in `lastDepositAttempt.error` field of payment object.

### Where to Find Errors

| Channel | Access |
|---|---|
| API | `GET /api/payment/{id}` → `lastDepositAttempt.error` |
| Dashboard | Payment details page |
| Webhooks | `payment_status_updated` payload |
| SDK | `onComplete` → `result.error.message` |

### Common Payment Errors

| Error Code | Description | Retryable? |
|---|---|---|
| `card_declined` | Card declined by bank | Yes |
| `insufficient_funds` | Not enough funds | Yes |
| `expired_card` | Card expired | No |
| `incorrect_cvc` | Wrong CVC | Yes |
| `incorrect_number` | Invalid card number | Yes |
| `invalid_cvc` | CVC format invalid | Yes |
| `invalid_expiry_month` | Invalid expiry month | Yes |
| `invalid_expiry_year` | Invalid expiry year | Yes |
| `invalid_number` | Card number format invalid | Yes |
| `processing_error` | Temporary issue | Yes |
| `generic_decline` | Generic decline | Yes |
| `do_not_honor` | Bank refused | Depends |
| `lost_card` | Card reported lost | No |
| `stolen_card` | Card reported stolen | No |
| `restricted_card` | Card has restrictions | No |
| `authentication_required` | 3DS needed | Yes |
| `withdrawal_count_limit_exceeded` | Transaction limit | Later |

### Last Deposit Attempt Object

```json
{
  "lastDepositAttempt": {
    "status": "failed",
    "amount": 4999,
    "paymentMethod": "CARD",
    "error": "card_declined",
    "attemptedAt": "2025-01-15T10:30:00.000Z"
  }
}
```

---

## SDK Error Handling

```javascript
onComplete: (result) => {
  if (result.error) {
    // result.error.message — Safe to display to customer
    // result.error.retryable — Whether customer can retry
    showError(result.error.message);
  }
}
```

SDK errors use customer-friendly, non-technical language.

---

## Best Practices

- Always check HTTP status code before parsing body
- Handle 401 by verifying API key configuration
- For 500, implement retry with exponential backoff
- Monitor failures via webhooks, not polling
- Display SDK `result.error.message` directly to customers
- Log raw `lastDepositAttempt.error` for internal monitoring
