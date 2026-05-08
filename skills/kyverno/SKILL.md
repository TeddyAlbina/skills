---
name: kyverno
description: kyverno is a Kubernetes-native policy engine designed for platform engineers to automate security, compliance, best practices, and governance. It treats policies as declarative Kubernetes resources and supports enforcement as an admission controller, CLI scanner, and at runtime. Kyverno also extends beyond Kubernetes to any JSON payload (Terraform, cloud resources, etc.).
---

**Kyverno** is a **Kubernetes-native policy engine** designed for platform engineers to automate security, compliance, best practices, and governance. It treats policies as declarative Kubernetes resources (`ClusterPolicy`, `Policy`, `ValidatingPolicy`, etc.) and supports enforcement as an admission controller, CLI scanner, and at runtime. Kyverno also extends beyond Kubernetes to any JSON payload (Terraform, cloud resources, etc.).

> **Official Sources**:
> - Introduction: https://kyverno.io/docs/introduction/
> - Policy Library: https://kyverno.io/policies/ (617+ ready-to-use policies)
> - Full Documentation: https://kyverno.io/docs/

---

## 1. What is Kyverno & Why Use It?

- **Declarative policies in YAML** (no new language to learn; supports JMESPath + CEL).
- **Four core operations**:
  - **Validate** – Block non-compliant resources.
  - **Mutate** – Auto-fix / inject defaults.
  - **Generate** – Auto-create companion resources (NetworkPolicies, RoleBindings, etc.).
  - **Cleanup** – Delete stale resources after TTL.
- **Image verification** (cosign, notary, etc.) for supply-chain security.
- **Policy reporting** (PolicyReport CRDs) + OpenReport format.
- **Policy exceptions** and background scanning.
- **CLI-first development** – test policies locally or in CI/CD before cluster deployment.

**Benefits**:
- Self-service for app teams while enforcing platform standards.
- GitOps-native (policies live in Git).
- High performance when written correctly (avoid wildcards).

---

## 2. Policy Types (from https://kyverno.io/policies/)

Policies are grouped by **action** and **domain** (Best Practices, AWS/EKS, Multi-Tenancy, Argo, etc.).

| Type       | Purpose                              | Common Use Cases                     |
|------------|--------------------------------------|--------------------------------------|
| **Validate** | Block bad configs                    | Labels, resources requests, deprecated APIs, security contexts |
| **Mutate**   | Auto-correct / inject                | Add labels/annotations, set defaults |
| **Generate** | Auto-create resources                | Default NetworkPolicy, RoleBindings per namespace |
| **Cleanup**  | Delete old resources                 | TTL-based cleanup of Jobs, PVCs     |
| **VerifyImages** | Image signature & vulnerability checks | Cosign, Notary, Trivy integration |

**CEL support** (Kubernetes 1.25+) is now preferred for new policies (`ValidatingPolicy` / `MutatingPolicy`).

---

## 3. Detailed Policy Samples (from https://kyverno.io/policies/)

### 3.1 Best Practices – Require Labels on Pods (CEL – ValidatingPolicy)

```yaml
apiVersion: policies.kyverno.io/v1
kind: ValidatingPolicy
metadata:
  name: require-labels
spec:
  evaluation:
    mode: "Kubernetes"
  matchConstraints:
    resourceRules:
      - apiGroups: [""]
        apiVersions: ["v1"]
        operations: ["CREATE", "UPDATE"]
        resources: ["pods"]
  variables:
    - name: "labels"
      expression: "object.metadata.?labels.orValue([])"
  validations:
    - message: "Pods must have 'app' and 'version' labels"
      expression: |
        has(variables.labels.app) &&
        has(variables.labels.version)
```

**What it does**: Enforces `app` and `version` labels on every Pod (great for observability and cost allocation).

### 3.2 Multi-Tenancy – Add Network Policy (Default Deny) (Generate – ClusterPolicy)

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: add-networkpolicy
  annotations:
    policies.kyverno.io/title: Add Network Policy
    policies.kyverno.io/category: Multi-Tenancy, EKS Best Practices
    policies.kyverno.io/subject: NetworkPolicy
    policies.kyverno.io/minversion: "1.6.0"
    policies.kyverno.io/description: >-
      By default, Kubernetes allows all Pod-to-Pod communication.
      This policy generates a default-deny NetworkPolicy for every new Namespace.
spec:
  rules:
    - name: default-deny
      match:
        any:
          - resources:
              kinds:
                - Namespace
      generate:
        apiVersion: networking.k8s.io/v1
        kind: NetworkPolicy
        name: default-deny
        namespace: "{{request.object.metadata.name}}"
        synchronize: true
        data:
          spec:
            podSelector: {}
            policyTypes:
              - Ingress
              - Egress
```

**What it does**: Zero-trust networking by default. Requires a CNI that supports NetworkPolicy (Calico, Cilium, etc.).

### 3.3 Other Popular Samples (descriptions + links)

- **Require Resource Limits** – Enforces CPU/memory requests/limits on containers.
- **Disallow Latest Tag** – Blocks `image: nginx:latest`.
- **Add Safe-to-Evict Annotation** – Mutates Pods with `hostPath`/`emptyDir` so Cluster Autoscaler can evict them.
- **Check Deprecated APIs** – Prevents use of removed Kubernetes APIs (e.g., `PodSecurityPolicy`).
- **Require IRSA for aws-node** – EKS-specific: forces IAM Roles for Service Accounts instead of the default highly-privileged SA.

**Full library**: https://kyverno.io/policies/ (filter by category/action). All policies are also in the public repo: https://github.com/kyverno/policies.

---

## 4. Kyverno CLI (Highly Recommended for Development)

**Purpose**: Test policies **before** they hit the cluster. Perfect for CI/CD.

### Installation
```bash
# Latest version (recommended)
curl -LO https://github.com/kyverno/kyverno/releases/latest/download/kyverno-cli.tar.gz
tar -xzf kyverno-cli.tar.gz && mv kyverno /usr/local/bin/
kyverno version
```

### Key Commands

| Command          | Usage                                                                 | Example |
|------------------|-----------------------------------------------------------------------|---------|
| `kyverno apply`  | Dry-run policies against resources                                    | `kyverno apply policy.yaml --resource deployment.yaml` |
| `kyverno test`   | Run full test suites (recommended for CI)                             | `kyverno test .` (looks for `kyverno-test.yaml`) |
| `kyverno jp`     | Debug JMESPath / CEL expressions                                      | `kyverno jp query -i pod.yaml 'metadata.labels.app'` |
| `kyverno create` | Scaffold new policies                                                 | `kyverno create policy ...` |
| `kyverno version`| Show CLI & compatible Kyverno version                                 | - |

**Workflow (Best Practice)**:
1. Write policy + `kyverno-test.yaml` (expected pass/fail results).
2. `kyverno test .` in CI.
3. `kyverno apply` for quick manual checks.
4. Commit → GitOps → Kyverno in cluster.

**Variables**:
```bash
kyverno apply policy.yaml --resource res.yaml --set image=nginx:1.25
```

---

## 5. Best Practices

1. **Start with `Audit` mode** (`validationFailureAction: Audit`) → observe reports → switch to `Enforce`.
2. **Validation before Mutation** – Never mutate without first validating the same rule.
3. **Be specific in `match`** – Never use `kinds: ["*"]` or broad wildcards. They kill performance.
4. **Use the CLI aggressively** – All policies should have accompanying tests.
5. **Namespace exclusions** – Always exclude `kube-system`, `kyverno`, and your GitOps namespaces.
6. **CEL over JMESPath** for new policies (cleaner, Kubernetes-native).
7. **Policy as Code** – Store in Git, use Kustomize/Helm for overlays (dev/staging/prod).
8. **Monitor metrics** – Admission count, CPU/memory, UpdateRequests backlog.
9. **3 replicas + PDB** for the admission controller in production.
10. **Separate controllers** – Scale admission, background, reports independently if needed.

---

## 6. Pitfalls to Avoid & How to Fix Them

| Pitfall                              | Symptom                              | How to Avoid / Fix |
|--------------------------------------|--------------------------------------|--------------------|
| **Wildcard policies**                | High CPU, API server throttling, OOM | Use explicit `kinds` + `namespaces` selectors. |
| **Fail-closed + Kyverno down**       | Entire cluster becomes un-deployable | Exclude system namespaces; run 3 replicas; have webhook deletion script ready. |
| **No background controller permissions** | Generate/Mutate rules silently fail | `kubectl auth can-i --as kyverno-background-controller create <resource>` |
| **AKS Admissions Enforcer loop**     | Webhook update loops                 | Add annotation `admissions.enforcer/disabled: "true"` (default in Helm ≥1.12). |
| **EKS/GKE network issues**           | Webhook timeouts                     | EKS: `hostNetwork: true`; GKE: firewall rule for port 9443. |
| **Too many reports**                 | etcd pressure, slow cluster          | Enable auto-deletion (Kyverno ≥1.10) or cron cleanup. |
| **Variables not substituted**        | Policy works in CLI but not cluster  | Use `dumpPayload: true` in policy or increase log verbosity (`-v=4`). |
| **Mutate idempotency issues**        | Repeated mutations on every apply    | Use `patchStrategicMerge` or conditions that are idempotent. |

**Quick recovery script** (if cluster is broken):
```bash
kubectl delete validatingwebhookconfiguration,mutatingwebhookconfiguration -l kyverno.io/webhook=kyverno
kubectl -n kyverno scale deployment kyverno-admission-controller --replicas=0
kubectl -n kyverno scale deployment kyverno-admission-controller --replicas=3
```

---

## 7. Additional Resources & Next Steps

- **Quick Start**: https://kyverno.io/docs/introduction/quick-start/
- **Policy Library**: https://kyverno.io/policies/
- **CLI Reference**: https://kyverno.io/docs/kyverno-cli/reference/kyverno/
- **Troubleshooting**: https://kyverno.io/docs/guides/troubleshooting/
- **Testing Guide**: https://kyverno.io/docs/guides/testing-policies/
- **GitHub Policies Repo**: https://github.com/kyverno/policies
- **Community**: Slack (kyverno) + GitHub Discussions

**Recommended Learning Path**:
1. Install Kyverno + CLI.
2. Apply 3–5 policies from the “Best Practices” category in Audit mode.
3. Write your first custom policy + test with CLI.
4. Move to Enforce + GitOps.

**Mastery achieved when**: You can write, test, and deploy a complex multi-rule policy (validate + mutate + generate) that passes `kyverno test` and runs safely in production.
