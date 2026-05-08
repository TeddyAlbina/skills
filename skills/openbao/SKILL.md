---
name: openbao
description: OpenBao is the **community-driven, Linux Foundation-hosted fork of HashiCorp Vault**. It delivers identical secrets-management power (dynamic secrets, KV, PKI, Transit, encryption-as-a-service, leasing/revocation) while remaining 100% open source (MPL 2.0). It is a **drop-in replacement** for Vault in most production environments..
---

**For AI Agents: Comprehensive OpenBao + Kubernetes Expertise Reference**  
*Version: OpenBao v2.5.2 (latest stable as of April 2026) + Kubernetes 1.28+*  
*Author: Senior Kubernetes & Security Architect (Grok)*  
*Last Updated: April 2026*  
*Sources: Official OpenBao Documentation (https://openbao.org/docs/), API (https://openbao.org/api-docs/), Helm Chart (https://github.com/openbao/openbao-helm), CSI Provider (https://github.com/openbao/openbao-csi-provider) + Source (https://github.com/openbao/openbao)*

OpenBao is the **community-driven, Linux Foundation-hosted fork of HashiCorp Vault**. It delivers identical secrets-management power (dynamic secrets, KV, PKI, Transit, encryption-as-a-service, leasing/revocation) while remaining 100% open source (MPL 2.0). It is a **drop-in replacement** for Vault in most production environments.

This file is your single source of truth for **using OpenBao in Kubernetes** — with full focus on secret injection into Pods, best practices, samples, and production pitfalls.

Every section includes:
- Core explanation
- Real-world examples (YAML + `bao` CLI + Helm + kubectl)
- Advice & Best Practices
- Points of Attention / Pitfalls
- References

---

## 1. OpenBao Overview & Architecture

**Core Concepts** (identical to Vault):
- **Server** (bao binary) — stores encrypted data, enforces policies.
- **Secret Engines** — KV v2 (static), Database (dynamic creds), PKI, Transit, AWS, Kubernetes, etc.
- **Auth Methods** — Kubernetes (ServiceAccount JWT), JWT/OIDC, AppRole, etc.
- **Policies** (HCL) — least-privilege ACLs.
- **Tokens** — short-lived, renewable, revocable.

**Data flow**:
```
Pod → Kubernetes Auth (JWT) → OpenBao → Policy → Secret Engine → Dynamic/Static secret
```

**Kubernetes-native integrations**:
1. **OpenBao Agent Injector** (mutating webhook + sidecar) — injects secrets as files/env vars.
2. **OpenBao CSI Provider** (with Secrets Store CSI Driver) — mounts secrets as CSI volumes (preferred modern approach).

**Advice**:
- Run OpenBao in **HA mode** with integrated Raft storage or external backend (etcd/Consul).
- Always use TLS + mTLS where possible.
- Prefer **dynamic secrets** over static whenever possible.

**References**:
- https://openbao.org/docs/
- https://github.com/openbao/openbao

---

## 2. Deploying OpenBao in Kubernetes (Recommended: Helm Chart)

The **official OpenBao Helm chart** (`openbao/openbao`) is the production way to install server + injector + CSI provider.

```bash
helm repo add openbao https://openbao.github.io/openbao-helm
helm repo update

helm install openbao openbao/openbao \
  --namespace openbao \
  --create-namespace \
  --set server.ha.enabled=true \
  --set server.ha.raft.enabled=true \
  --set injector.enabled=true \
  --set csi.enabled=true \
  --set server.dataStorage.size=50Gi
```

**Key production values.yaml snippet**:
```yaml
server:
  ha:
    enabled: true
    raft:
      enabled: true
  image:
    repository: openbao/openbao
    tag: "2.5.2"
injector:
  enabled: true
  replicas: 3
  # TLS handled automatically or via cert-manager
csi:
  enabled: true
```

**Advice**:
- Use `cert-manager` for injector TLS (see example in docs).
- Separate namespaces: `openbao` for server, application namespaces for workloads.
- Enable audit logging to a persistent volume or Loki.

**Points of Attention**:
- Helm chart is **not compatible with Helm v2**.
- First install requires manual unseal (or use auto-unseal with AWS KMS, GCP KMS, etc.).

**References**:
- https://openbao.org/docs/platform/k8s/helm/
- https://openbao.org/docs/platform/k8s/helm/examples/

---

## 3. Kubernetes Authentication Method

Pods authenticate to OpenBao using their **ServiceAccount token** (JWT).

```bash
# Inside OpenBao pod or via port-forward
bao auth enable kubernetes

bao write auth/kubernetes/config \
  kubernetes_host="https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_SERVICE_PORT" \
  kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
  token_reviewer_jwt=@/var/run/secrets/kubernetes.io/serviceaccount/token
```

**Role binding** (example for app `myapp`):
```bash
bao write auth/kubernetes/role/myapp \
  bound_service_account_namespaces=default,prod \
  bound_service_account_names=sa-myapp \
  policies=myapp-policy \
  ttl=1h
```

**Best Practice**: One dedicated ServiceAccount + Role per application.

---

## 4. Detailed Secret Injection into Pods (Two Production Methods)

### 4.1 Method 1: OpenBao Agent Injector (Sidecar + Mutating Webhook) — Classic & Flexible

The injector **automatically injects** an OpenBao Agent sidecar into annotated Pods. The sidecar fetches secrets at startup and on renewal, then writes them to an in-memory volume (ephemeral, never persisted in etcd).

**How it works step-by-step**:
1. Pod is created with annotations.
2. Mutating webhook (injector) adds:
   - OpenBao Agent sidecar container.
   - EmptyDir volume for secrets.
3. Agent authenticates via Kubernetes auth.
4. Agent renders templates or raw secrets into the volume.
5. Main container consumes secrets from `/vault/secrets/` or as env vars.

**Example Pod annotations + YAML**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
  annotations:
    openbao.hashicorp.com/agent-inject: "true"                  # Enable injection
    openbao.hashicorp.com/agent-inject-secret-db-creds: "secret/data/myapp/db"   # Path to secret
    openbao.hashicorp.com/agent-inject-template-db-creds: |
      {{- with secret "secret/data/myapp/db" }}
      DB_USER={{ .Data.data.username }}
      DB_PASS={{ .Data.data.password }}
      {{- end }}
    openbao.hashicorp.com/role: "myapp"                         # Auth role
    openbao.hashicorp.com/agent-inject-command: "echo 'secrets refreshed'"  # Optional post-render hook
spec:
  serviceAccountName: sa-myapp
  containers:
  - name: myapp
    image: myapp:latest
    envFrom:
    - secretRef:
        name: db-creds   # Optional: injector can also create K8s Secret
    volumeMounts:
    - name: secrets
      mountPath: /secrets
      readOnly: true
  volumes:
  - name: secrets
    emptyDir:
      medium: Memory
```

**Best Practices**:
- Use **templates** for complex rendering (JSON, env files, config files).
- Set `openbao.hashicorp.com/agent-inject-secret-<name>` for multiple secrets.
- Prefer files over env vars (safer for multi-line secrets).
- Short TTLs + auto-renewal.

**Points of Attention**:
- Secrets live only in memory inside the Pod (great for security).
- Sidecar adds ~50-100ms startup latency.
- Requires the injector deployment to be healthy.

### 4.2 Method 2: OpenBao CSI Provider + Secrets Store CSI Driver (Modern & Recommended)

Secrets are mounted **directly as CSI volumes** — no sidecar, no etcd storage of secrets.

**Installation** (already enabled via Helm):
- Secrets Store CSI Driver (official Kubernetes SIG)
- OpenBao CSI Provider (`openbao-csi-provider`)

**SecretProviderClass YAML** (dynamic DB creds example):
```yaml
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: openbao-db-creds
  namespace: prod
spec:
  provider: openbao
  parameters:
    objects: |
      - objectName: "db-creds"
        objectType: "kv-v2"
        objectPath: "secret/data/myapp/db"
        objectVersion: "latest"
        objectAlias: "DB_CREDS"   # Optional
```

**Pod usage**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-csi
spec:
  serviceAccountName: sa-myapp
  containers:
  - name: myapp
    image: myapp:latest
    volumeMounts:
    - name: openbao-secrets
      mountPath: "/secrets"
      readOnly: true
  volumes:
  - name: openbao-secrets
    csi:
      driver: secrets-store.csi.k8s.io
      readOnly: true
      volumeAttributes:
        secretProviderClass: "openbao-db-creds"
```

**Best Practices**:
- Use CSI for **new deployments** — cleaner, lower overhead, native Kubernetes.
- Combine with `syncSecret` feature if you need a Kubernetes Secret.
- Great for init containers or apps that read from filesystem.

**Points of Attention**:
- Secrets are **not** auto-refreshed on rotation (Pod restart required unless using rotation webhook).
- Requires Secrets Store CSI Driver installed cluster-wide.

**References**:
- https://openbao.org/docs/platform/k8s/csi/
- https://openbao.org/docs/platform/k8s/csi/examples/
- https://github.com/openbao/openbao-csi-provider


---

## 5. Integrating OpenBao with cert-manager (Production-Grade TLS & PKI)

cert-manager and OpenBao are a **perfect pair** in Kubernetes:
- **cert-manager → OpenBao**: Use OpenBao’s PKI secret engine as a CA backend so cert-manager can issue/renew certificates for Ingress, mTLS, service mesh, etc.
- **OpenBao → cert-manager**: Use cert-manager to automatically provision and rotate TLS certificates for the **OpenBao Agent Injector webhook** (required for HA injector replicas).

Both integrations are **fully supported** because OpenBao maintains 100% Vault API compatibility.

### 5.1 Use Case 1: cert-manager securing OpenBao (Injector Webhook TLS)
The most common and **officially documented** integration. Enables multiple injector replicas and automatic certificate rotation.

**Why?** The mutating webhook needs a valid TLS certificate. cert-manager handles issuance + renewal automatically.

**Official Step-by-Step (from openbao.org/docs)**:

#### Prerequisites
Install cert-manager (if not present):
```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true
```

 
**1. Create CA Issuer + CA Certificate (in `openbao` namespace)**


```yaml
# ca-issuer.yaml
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: selfsigned
spec:
  selfSigned: {}
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: injector-selfsigned-ca
spec:
  isCA: true
  commonName: Agent Inject CA
  secretName: injector-ca-secret
  duration: 87660h   # 10 years
  privateKey:
    algorithm: ECDSA
    size: 256
  issuerRef:
    name: selfsigned
    kind: Issuer
    group: cert-manager.io
---
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: injector-ca-issuer
spec:
  ca:
    secretName: injector-ca-secret
```

Apply:

```bash
kubectl apply -n openbao -f ca-issuer.yaml
```


**2. Create Injector Certificate (signed by the CA)**

```yaml
# injector-certificate.yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: injector-certificate
spec:
  secretName: injector-tls
  duration: 24h
  renewBefore: 144m   # ~10% of duration
  dnsNames:
  - openbao-agent-injector-svc
  - openbao-agent-injector-svc.openbao
  - openbao-agent-injector-svc.openbao.svc
  issuerRef:
    name: injector-ca-issuer
    kind: Issuer
  commonName: Agent Inject Cert
```

Apply:

```bash
kubectl apply -n openbao -f injector-certificate.yaml
```

**3. Install/Upgrade OpenBao Helm Chart with cert-manager references**

```bash
helm install openbao openbao/openbao \
  --namespace openbao \
  --set injector.replicas=2 \
  --set injector.leaderElector.enabled=false \
  --set injector.certs.secretName=injector-tls \
  --set injector.webhook.annotations="cert-manager.io/inject-ca-from: {{ .Release.Namespace }}/injector-certificate"
```

**Best Practices**:

Short-lived injector cert (24h) + auto-renewal.
- Use `dnsNames` **exactly** as shown — they must match the Kubernetes service DNS.
- Monitor cert-manager Certificate resources with `kubectl get certificate -n openbao`.

**Points of Attention**:
- Certificate must exist before Helm install (or use `--wait`).
- For production, use a real CA Issuer (Let’s Encrypt, Venafi, or OpenBao PKI itself — see 5.2).

**References**:
- Official: https://openbao.org/docs/platform/k8s/helm/examples/injector-tls-cert-manager/



### 5.2 Use Case 2: OpenBao PKI as CA backend for cert-manager (VaultIssuer)
Use OpenBao’s **PKI secret engine** to issue certificates via cert-manager. Perfect for internal mTLS, service mesh, Ingress, etc.

**Setup in OpenBao** (PKI engine):

```bash
bao secrets enable pki
bao write pki/root/generate/internal \
  common_name="openbao.internal" \
  ttl=87600h   # 10 years
bao write pki/roles/internal \
  allowed_domains="internal" \
  allow_subdomains=true \
  max_ttl="720h"
```

**cert-manager ClusterIssuer / Issuer** (VaultIssuer):

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: openbao-pki-issuer
spec:
  vault:
    server: "https://openbao.openbao.svc:8200"   # or external URL
    path: "pki/issue/internal"                   # role path
    auth:
      tokenSecretRef:
        name: openbao-token-secret
        key: token
    caBundle: |                                  # Base64 of OpenBao CA (optional)
      LS0t...
```

**Sample Certificate request** (for an app):

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: myapp-tls
  namespace: prod
spec:
  secretName: myapp-tls-secret
  duration: 720h
  renewBefore: 168h
  dnsNames:
  - myapp.prod.svc.cluster.local
  issuerRef:
    name: openbao-pki-issuer
    kind: ClusterIssuer
```

**Best Practices**:
- Prefer **short TTLs** (hours/days) + auto-renewal.
- Use OpenBao **Transit** or **PKI** for encryption-as-a-service.
- Store the Vault token in a Kubernetes Secret (rotate frequently).
- Combine with External Secrets Operator if needed.

**Points of Attention**:
- OpenBao must be reachable from cert-manager pods (NetworkPolicy).
- Use mTLS between cert-manager and OpenBao for extra security.
- Revocation is automatic via OpenBao CRL/OCSP.

**References**:
- cert-manager Vault docs (works identically): https://cert-manager.io/docs/configuration/vault/
- OpenBao PKI: https://openbao.org/docs/secrets/pki/



---

## 6. Best Practices (Kubernetes Context)

1. **Always use cert-manager for injector** TLS in HA setups.
2. **Prefer OpenBao PKI + cert-manager** over static certs for all internal workloads.
3. Least Privilege + short TTLs + dynamic secrets.
4. CSI Provider for secret injection (no sidecar) + cert-manager for TLS.
5. Audit logging + Prometheus alerts on certificate expiry and OpenBao health.

**Platform Advice**:
- Use External Secrets Operator (ESO) as alternative to CSI if you prefer Kubernetes Secrets synced from OpenBao.
- Combine with Kyverno/Gatekeeper policies to enforce annotations.

---

## 7. Common Pitfalls & Troubleshooting

| Pitfall                        | Symptom                          | Fix / Prevention                              |
|--------------------------------|----------------------------------|-----------------------------------------------|
| Wrong dnsNames in Certificate    | Webhook TLS errors             | Match exact service DNS pattern               |
| cert-manager not ready    | Injector fails to start               | Use `--wait` or dependency in GitOps          |
| Missing injector-ca-issuer    | Certificate stuck in Pending      | Apply CA resources first                      |
| VaultIssuer token expired    | cert-manager fails to issue cert   | Use short-lived tokens + rotation             |
| Wrong auth role / namespace    | 403 Forbidden                    | Check `bound_service_account_namespaces`      |
| Injector TLS mismatch          | Webhook fails                    | Use cert-manager example in Helm              |
| CSI Provider not installed     | Volume mount fails               | Enable in Helm + install Secrets Store Driver |
| Static secrets in etcd         | Compliance violation             | Use CSI or Agent (ephemeral)                  |
| Long-lived tokens              | Security risk                    | Enforce TTL ≤ 1h                              |
| No audit logs                  | No visibility on secret access   | Always enable `audit` device                  |

**Useful debug commands**:
```bash
kubectl get certificate -n openbao -o wide
kubectl describe certificate injector-certificate -n openbao
bao read pki/cert/ca   # check OpenBao PKI root
```

---

## 8. Advanced Topics & Extensibility

- **Kubernetes Secrets Engine** — Generate K8s ServiceAccount tokens from OpenBao (use with caution).
- **Transit Engine** — Encrypt/decrypt data without storing it.
- **PKI** — Issue short-lived certs for mTLS.
- **Multi-cluster** — Use replication or federated OpenBao.
- **Policy as Code** — Sentinel (if using Enterprise features) or OPA.

**GitHub Exploration**:
- Core: `https://github.com/openbao/openbao`
- Helm: `https://github.com/openbao/openbao-helm`
- CSI: `https://github.com/openbao/openbao-csi-provider`

---

## 9. References & Learning Path

**Official**:
- https://openbao.org/docs/platform/k8s/
- https://openbao.org/docs/auth/kubernetes/
- https://openbao.org/docs/secrets/kubernetes/
- https://openbao.org/api-docs/

**cert-manager + OpenBao resources**:
- https://openbao.org/docs/platform/k8s/helm/examples/injector-tls-cert-manager/
- https://cert-manager.io/docs/configuration/vault/
- https://openbao.org/docs/secrets/pki/

**Tools**:
- `bao` CLI (replaces `vault`)
- Helm chart + cert-manager
- Secrets Store CSI Driver + OpenBao CSI Provider

**How to use this file as an AI agent**:
1. Always prefer **CSI Provider** for new apps.
2. For legacy apps needing templates → use **Agent Injector**.
3. Generate manifests with exact annotations above.
4. Validate with `bao` CLI and `kubectl describe`.
