# Payouts & Balance

## Balance

Your Inflow balance holds funds from successful payments. Balance is in USD (payments in EUR are converted).

```bash
curl https://api.inflowpay.xyz/api/account/balance \
  -H "X-Inflow-Api-Key: inflow_prod_your_key"
```

---

## Payout Destinations

### Bank Accounts

Supported currencies: EUR, GBP, USD

```bash
# Get required fields for a country
curl https://api.inflowpay.xyz/api/account/bank-form?country=FR \
  -H "X-Inflow-Api-Key: inflow_prod_your_key"

# Register bank account
curl -X POST https://api.inflowpay.xyz/api/account/bank \
  -H "X-Inflow-Api-Key: inflow_prod_your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "country": "FR",
    "currency": "EUR",
    "iban": "FR7630006000011234567890189",
    "bic": "BNPAFRPPXXX",
    "holderName": "John Doe"
  }'
```

### Crypto Wallets

Supported: USDC on Polygon, Ethereum, Base, Starknet, Solana

```bash
# Get available networks
curl https://api.inflowpay.xyz/api/account/wallet-networks \
  -H "X-Inflow-Api-Key: inflow_prod_your_key"

# Register wallet
curl -X POST https://api.inflowpay.xyz/api/account/wallet \
  -H "X-Inflow-Api-Key: inflow_prod_your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "0x...",
    "label": "My USDC Wallet"
  }'
```

Network is inferred from wallet address.

### Manage Destinations

```bash
# List all
curl https://api.inflowpay.xyz/api/account/accounts \
  -H "X-Inflow-Api-Key: inflow_prod_your_key"

# Get by ID
curl https://api.inflowpay.xyz/api/account/accounts/{accountId} \
  -H "X-Inflow-Api-Key: inflow_prod_your_key"

# Archive
curl -X DELETE https://api.inflowpay.xyz/api/account/accounts/{accountId} \
  -H "X-Inflow-Api-Key: inflow_prod_your_key"
```

---

## Get Payout Quote

```bash
curl https://api.inflowpay.xyz/api/account/quote?accountId={accountId} \
  -H "X-Inflow-Api-Key: inflow_prod_your_key"
```

Returns fees and exchange rate (if applicable).

---

## Initiate Payout

```bash
curl -X POST https://api.inflowpay.xyz/api/account/payout \
  -H "X-Inflow-Api-Key: inflow_prod_your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": "acct_xyz789",
    "amount": 50000
  }'
```

---

## Virtual IBANs

Receive funds via EUR or USD virtual IBANs. EUR settles to EURC on Base, USD settles to USDC on Base.

```bash
# Create virtual account
curl -X POST https://api.inflowpay.xyz/api/virtual-account \
  -H "X-Inflow-Api-Key: inflow_prod_your_key" \
  -H "Content-Type: application/json" \
  -d '{ "currency": "EUR" }'

# List virtual accounts
curl https://api.inflowpay.xyz/api/virtual-account \
  -H "X-Inflow-Api-Key: inflow_prod_your_key"
```

Max one virtual account per currency per merchant.

---

## 3rd Party Payouts

Payout to vendors, contractors, or service providers by adding their bank/wallet as a destination.

---

## Yield on Balance

Optional yield on idle balance. Currently paused, expected to be re-enabled soon.

---

## Global Coverage

### Bank Payout Networks

| Currency | Network |
|---|---|
| EUR | SEPA |
| GBP | Faster Payments |
| USD | ACH |

### Crypto Networks

| Network | Token |
|---|---|
| Polygon | USDC |
| Ethereum | USDC |
| Base | USDC |
| Starknet | USDC |
| Solana | USDC |

---

## Connect: Sub-merchant Payouts

Use `X-On-Behalf-Of` to manage payouts for sub-merchants:

```bash
curl -X POST https://api.inflowpay.xyz/api/account/payout \
  -H "X-Inflow-Api-Key: inflow_prod_your_key" \
  -H "X-On-Behalf-Of: sub_abc123" \
  -H "Content-Type: application/json" \
  -d '{ "accountId": "acct_xyz", "amount": 50000 }'
```
