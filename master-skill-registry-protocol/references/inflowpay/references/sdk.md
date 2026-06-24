# SDK Integration

## Overview

The `@inflow_pay/sdk` package provides an iframe-based card payment form. Card details never touch your servers — PCI compliance handled by Inflow.

**npm:** `npm install @inflow_pay/sdk`
**CDN:** `https://cdn.jsdelivr.net/npm/@inflow_pay/sdk/dist/sdk.umd.js`

**Requirements:** React >= 16.8.0 or any modern browser. Backend endpoint to create payments with private key.

---

## React Integration

```tsx
import { InflowPayProvider, CardElement, PaymentResultStatus } from '@inflow_pay/sdk/react';

function Checkout() {
  const [paymentId, setPaymentId] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/create-payment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: 'customer@example.com', country: 'FR' })
    })
      .then(res => res.json())
      .then(data => setPaymentId(data.paymentId));
  }, []);

  if (!paymentId) return <div>Loading...</div>;

  return (
    <InflowPayProvider config={{ publicKey: 'inflow_pub_xxx' }}>
      <CardElement
        paymentId={paymentId}
        onComplete={(result) => {
          if (result.status === PaymentResultStatus.SUCCESS) {
            setTimeout(() => window.location.href = '/confirmation', 2000);
          }
          if (result.error) {
            console.error(result.error.message);
          }
        }}
        style={{
          fontFamily: 'Inter',
          button: {
            backgroundColor: '#0070F3',
            textColor: '#FFFFFF',
            borderRadius: '8px'
          }
        }}
        buttonText="Pay €49.99"
      />
    </InflowPayProvider>
  );
}
```

### Next.js App Router

```tsx
'use client';

import { InflowPayProvider, CardElement } from '@inflow_pay/sdk/react';
```

---

## Vanilla JS Integration

### npm

```javascript
import { InflowPayProvider } from '@inflow_pay/sdk';

const provider = new InflowPayProvider({
  config: { publicKey: 'inflow_pub_xxx' }
});

provider.createCardElement({
  paymentId: 'pay_abc123',
  container: '#card-container',
  onComplete: (result) => {
    if (result.status === 'SUCCESS') {
      alert('Payment successful!');
    }
  }
}).mount();
```

### CDN

```html
<script src="https://cdn.jsdelivr.net/npm/@inflow_pay/sdk/dist/sdk.umd.js"></script>
<div id="card-container"></div>
<script>
  const provider = new InflowPaySDK.InflowPayProvider({
    config: { publicKey: 'inflow_pub_xxx' }
  });

  provider.createCardElement({
    paymentId: 'pay_abc123',
    container: '#card-container',
    onComplete: (result) => {
      if (result.status === 'SUCCESS') {
        alert('Payment successful!');
      }
    }
  }).mount();
</script>
```

---

## InflowPayProvider Props

| Prop | Type | Required | Description |
|---|---|---|---|
| `config.publicKey` | string | Yes | Public API key (`inflow_pub_xxx`) |
| `config.locale` | string | No | `en`, `de`, `es`, `fr`, `it`, `nl`, `pl`, `pt` |

## CardElement Props

| Prop | Type | Required | Description |
|---|---|---|---|
| `paymentId` | string | Yes | Payment ID from backend |
| `onComplete` | function | No | Called on success/failure |
| `onError` | function | No | Called on SDK errors |
| `onReady` | function | No | Called when form is mounted |
| `onChange` | function | No | Called on validation state change |
| `showDefaultSuccessUI` | boolean | No | Show built-in success screen (default: true) |
| `style` | object | No | Custom styling |
| `buttonText` | string | No | Custom submit button text |
| `placeholders` | object | No | Custom input placeholders |

---

## Payment Result

```typescript
interface PaymentResult {
  status: 'SUCCESS' | 'FAILED';
  paymentId: string;
  error?: {
    code: string;
    message: string;
    retryable: boolean;
  };
}
```

---

## Styling & Customization

```javascript
style={{
  fontFamily: 'Inter',
  backgroundColor: '#ffffff',
  textColor: '#000000',
  button: {
    backgroundColor: '#0070F3',
    textColor: '#FFFFFF',
    borderRadius: '8px',
    fontSize: '16px'
  },
  input: {
    borderColor: '#e0e0e0',
    borderRadius: '4px',
    fontSize: '14px'
  }
}}
```

---

## 3D Secure

3DS is handled automatically by the SDK. When required:

1. SDK shows 3DS challenge in an iframe
2. Customer authenticates with their bank
3. SDK completes the payment
4. `onComplete` fires with result

### 3DS Test Cards (SDK only)

| Card Number | Brand | Scenario |
|---|---|---|
| `5204247750001471` | Mastercard | Successful Frictionless |
| `6011601160116011` | Discover | Successful Frictionless |
| `340000000004001` | Amex | Successful Frictionless |
| `4000020000000000` | Visa | Successful Challenge |
| `370000000000002` | Amex | Successful Challenge |
| `4111111111111111` | Visa | Attempted — succeeds |
| `4264281511112228` | Visa | Failed — declined |
| `5424180000000171` | Mastercard | Failed — declined |

---

## Security

| Feature | Description |
|---|---|
| PCI Compliant | Card data tokenized in secure iframe |
| Iframe Isolation | Sandboxed from page JavaScript |
| HTTPS Only | All communication encrypted |
| Public Key Only | Frontend uses safe-to-expose key |
| Tokenization | Card details tokenized before processing |

> **Never expose your private API key** in frontend code.
