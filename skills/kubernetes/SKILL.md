---
name: kubernetes
description: Kubernetes architecture, deployment, management, and troubleshooting. Activate for k8s, kubectl, pods, deployments, services, ingress, namespaces, and container orchestration tasks.
---

# Kubernetes Skill

Provides comprehensive Kubernetes deployment and management capabilities for the Golden Armada AI Agent Fleet Platform.

# Kubernetes Skills Guide

**For AI Agents: Comprehensive Kubernetes Expertise Reference**  
*Version: Kubernetes v1.35 (latest patch v1.35.3 as of March 2026)*  
*Author: Senior Kubernetes Architect (Grok)*  
*Last Updated: April 2026*  
*Sources: Official Kubernetes Documentation (kubernetes.io/docs) + Source Code (github.com/kubernetes/kubernetes)*

This file distills **decades of production-grade Kubernetes architecture, operations, and deep-dive knowledge** into a single, actionable reference. Use it to reason about clusters, generate manifests, debug issues, design platforms, or implement GitOps. Every section includes:

- **Core explanation**  
- **Real-world examples** (YAML + kubectl)  
- **Advice & Best Practices**  
- **Points of Attention / Pitfalls**  
- **References** (docs + GitHub paths)

**Guiding Principles**:
- Design for Failure: Always assume nodes, networks, and pods will fail.
- Declarative over Imperative: Rely on GitOps and declarative manifests.
- Least Privilege: Enforce strict RBAC, Pod Security Standards, and Network Policies.
- Extensibility: Leverage the Controller pattern, CRDs, and the Gateway API instead of fighting core objects.

---

## 1. Cluster Architecture & Components

A Kubernetes cluster = **Control Plane** + **Node(s)**. The control plane maintains desired state; nodes run workloads.

### Control Plane Components
- **kube-apiserver**: Front-end for the Kubernetes API (HTTP REST). All clients (kubectl, controllers, users) talk to it.  
- **etcd**: Consistent, highly-available key-value store for all cluster data (state, configuration, secrets).  
- **kube-scheduler**: Watches unscheduled Pods and binds them to nodes based on constraints, resources, affinity, taints, etc.  
- **kube-controller-manager**: Runs core controllers (Deployment, ReplicaSet, Node, etc.).  
- **cloud-controller-manager** (optional): Cloud-specific logic (LoadBalancers, routes, volumes).

### Node Components
- **kubelet**: Agent on every node. Registers node with API server, watches Pods, launches containers via CRI, reports status.  
- **kube-proxy**: Maintains network rules for Services (iptables, IPVS, or eBPF mode).  
- **Container Runtime**: CRI-compatible (containerd, CRI-O).  

**Addons** (DNS, monitoring, logging, CNI) extend functionality.

**Advice**:
- Run control plane with **3–5 etcd members** (odd number) for HA in production.
- Separate control-plane nodes from worker nodes (use `node-role.kubernetes.io/control-plane` taint).
- Prefer managed control planes (EKS, GKE, AKS) unless you need full control.

**Points of Attention**:
- etcd is the **single source of truth** — back it up regularly (`etcdctl snapshot save`).
- kube-apiserver is CPU/memory intensive; scale vertically or horizontally with multiple instances.
- Never expose etcd to the internet.

**References**:
- [Cluster Architecture](https://kubernetes.io/docs/concepts/architecture/)  
- [Components](https://kubernetes.io/docs/concepts/overview/components/)  
- GitHub: `pkg/kubelet/`, `pkg/scheduler/`, `cmd/kube-apiserver/`, `staging/src/k8s.io/apiserver/`

---

## 2. Core Kubernetes Objects & Workloads

### Pods (Smallest Deployable Unit)
A Pod = 1+ co-located containers sharing network namespace + storage volumes + IPC. IP is shared; containers talk via `localhost`.

**Example YAML** (single-container):
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
  labels:
    app: web
spec:
  containers:
  - name: nginx
    image: nginx:1.25
    ports:
    - containerPort: 80
    resources:
      requests:
        cpu: "100m"
        memory: "128Mi"
      limits:
        cpu: "500m"
        memory: "512Mi"
    readinessProbe:
      httpGet:
        path: /
        port: 80
```

**Multi-container example**: Sidecar pattern (e.g., logging agent).
**Advice**:

**Never** create bare Pods in production. Use controllers (Deployment, StatefulSet, DaemonSet, Job, CronJob).
Always set **resource requests + limits** (CPU throttling & OOMKills are real).
Use `initContainers` for one-time setup, `ephemeralContainers` for debugging.

**Points of Attention**:

Pods are **ephemeral** - design for immutability.
Pod template changes → new Pods (no in-place mutation except limited fields).
Static Pods (manifests in `/etc/kubernetes/manifests`) bypass API server.

**References**:

- Pods: https://kubernetes.io/docs/concepts/workloads/pods/
- GitHub: `pkg/kubelet/pod/`

## Deployments (Stateless Workloads)

Manages ReplicaSets → Pods with declarative rolling updates.
**Example** (with rolling update strategy):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  replicas: 5
  selector:
    matchLabels:
      app: frontend
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 25%
      maxSurge: 25%
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: app
        image: myapp:v1.2.3
```

**Advice**:

Use `revisionHistoryLimit`: 10 for rollbacks (`kubectl rollout undo`).
Combine with HorizontalPodAutoscaler (HPA) for CPU/Memory or custom metrics.

**Points of Attention**:

Selector is `immutable` after creation.
Do **not** manually edit owned ReplicaSets.
Rollouts can stall — watch `progressDeadlineSeconds`.

**References**:

- Deployments: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/

### Other Workloads

- **StatefulSet**: Ordered, stable identity + persistent storage (headless Service + PVC templates).
- **DaemonSet**: One Pod per node (node agents, CNI, monitoring).
- **Job / CronJob**: Batch / scheduled workloads.

**Advice**: StatefulSet for databases, Kafka, etc. Use `volumeClaimTemplates`.

---

## 3. Networking
### Services
Abstracts Pod IPs. DNS: `my-service.my-ns.svc.cluster.local`.

**Types**:
- `ClusterIP` (default, internal)
- `NodePort` (high-port on every node)
- `LoadBalancer` (cloud LB)
- `ExternalName` (CNAME)

**Example** (headless for StatefulSet):

```yaml
apiVersion: v1
kind: Service
metadata:
  name: db
spec:
  clusterIP: None
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

**Advice**:
- Prefer **Gateway API for** external HTTP/HTTPS traffic.
- Use `internalTrafficPolicy: Local` + `externalTrafficPolicy: Local` to preserve source IP.

**Points of Attention**:
- Services without selectors require manual EndpointSlices.
- `loadBalancerIP` is deprecated — use annotations.
- Headless Services return Pod IPs directly in DNS.

**References**:
- Services https://kubernetes.io/docs/concepts/services-networking/service/

### Network Policies & CNI
-** NetworkPolicy**: Allow/Deny traffic at Pod level (egress/ingress, port, namespace).
- CNI plugins (Calico, Cilium, Flannel) implement pod-to-pod networking.

**Advice**: Always apply a default-deny policy in production namespaces.

**References**:
- Network Policies https://kubernetes.io/docs/concepts/services-networking/network-policies/

---

## 4. Storage
- **PersistentVolume (PV)** + **PersistentVolumeClaim (PVC)**.
- **StorageClass** for dynamic provisioning.
- **CSI** (Container Storage Interface) is the standard.

**Advice**:
- Use s`torageClassName` + `accessModes: ReadWriteOnce` (most common).
- For databases: `volumeBindingMode: WaitForFirstConsumer` + topology-aware scheduling.

** Points of Attention**:
- PVCs are **namespace-scoped**; PVs are cluster-scoped.
- Deleting PVC does **not** always delete PV (depends on reclaim policy).

References:
- Storage https://kubernetes.io/docs/concepts/storage/

---

## 5. Configuration & Secrets
- **ConfigMap**: Non-sensitive config.
- **Secret**: Base64-encoded sensitive data (use `stringData` for readability).

**Advice**:
- External Secrets Operator or Sealed Secrets for GitOps.
- Mount as volumes (preferred over env vars) to avoid restart on change.

**Points of Attention**:
- Secrets are **not encrypted by default** in etcd — enable encryption at rest.

References:
- Secrets Good Practices https://kubernetes.io/docs/concepts/security/secrets-good-practices/

---

## 6. Security (Zero-Trust Mindset)
**Key Layers**:

- RBAC + ServiceAccounts (least privilege).
- Pod Security Standards (Restricted is default in 1.35+).
- NetworkPolicy + RuntimeClasses.
- Admission webhooks (OPA/Gatekeeper, Kyverno).
- Image scanning + signed images.

**Advice**:
- Run as non-root (`runAsNonRoot: true`).
- Use `seccompProfile: RuntimeDefault`.
- Enable audit logging + `ValidatingAdmissionPolicy`.

**Points of Attention**:
- Default ClusterRoleBinding cluster-admin is extremely powerful — audit regularly.
- etcd data is plaintext unless encrypted.

References:
- Security Overview https://kubernetes.io/docs/concepts/security/
- RBAC Good Practices https://kubernetes.io/docs/concepts/security/rbac-good-practices/
- Security Checklist https://kubernetes.io/docs/concepts/security/security-checklist/

--

## 7. Trivy: All-in-One Security Scanner for Kubernetes & Containers
**Trivy** (by Aqua Security) is the **most popular open-source security scanner** for container images, filesystems, Git repositories, SBOMs, IaC, clouds, **and Kubernetes clusters**. It detects:
- **Vulnerabilities** (OS packages + language dependencies)
- **Misconfigurations** (including Kubernetes resources vs. CIS/NSA/PSS benchmarks)
- **Secrets** (exposed credentials)
- **Licenses**
- **SBOM generation & scanning**

**Current safe version (April 2026)**: **v0.69.3** (v0.69.4 was part of a February 2026 GitHub Actions supply-chain compromise — **always verify releases and use only official/safe versions**).

Trivy is **lightweight, fast, accurate**, and has **zero external dependencies** for most scans. It is the de-facto standard for **shift-left security** in Kubernetes platforms.

### 7.1 Installation
**Official methods** (preferred):
```bash
# macOS / Linux
brew install trivy

# One-liner install (specific version)
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sudo sh -s -- -b /usr/local/bin v0.69.3

# Docker (recommended in CI/CD)
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  -v $HOME/.cache/trivy:/root/.cache/ aquasec/trivy:0.69.3 image nginx:latest
```

**Kubernetes-specific**:
- **Trivy CLI** (for ad-hoc / CI)
- **Trivy Operator** (Helm-installed inside cluster for continuous scanning – see below)


###  7.2 Core CLI Commands & Examples
**Container Image Scanning (most common)**

```bash
# Basic scan
trivy image nginx:1.25

# Fail build on HIGH/CRITICAL + ignore unfixed
trivy image --exit-code 1 --severity HIGH,CRITICAL --ignore-unfixed myapp:v1.2.3

# JSON output for CI
trivy image --format json --output trivy-report.json myapp:v1.2.3

# With custom policy (Rego)
trivy image --ignore-policy ./policy.rego myapp:latest
```

**Kubernetes Cluster Scanning** (`trivy k8s`)

```bash
# Summary report of entire cluster
trivy k8s --report summary

# Full compliance (CIS Kubernetes Benchmark)
trivy k8s --compliance k8s-cis-1.23 --report all

# NSA/CISA Hardening Guidance
trivy k8s --compliance k8s-nsa-1.0 --report summary

# Pod Security Standards
trivy k8s --compliance k8s-pss-restricted-0.1 --report summary

# Generate & scan KBOM (Kubernetes Bill of Materials)
trivy k8s --format cyclonedx --output kbom.cdx.json
trivy sbom kbom.cdx.json
```

**Filters & advanced flags**:
- `--exclude-namespaces dev,staging`
- `--severity CRITICAL`
- `--scanners vuln,config,secret`
- `--skip-images` (scan only cluster config)

**Filesystem / Repo Scanning**

```bash
trivy fs .                  # Current directory
trivy repo https://github.com/myorg/myapp
```

### 7.3 Trivy Operator (In-Cluster Continuous Scanning)
**Deploy via Helm (recommended)**:

```bash
helm repo add aqua https://aquasecurity.github.io/helm-charts/
helm repo update
helm install trivy-operator aqua/trivy-operator \
  --namespace trivy-system \
  --create-namespace \
  --set trivy.ignoreUnfixed=true \
  --set trivy.severity=HIGH,CRITICAL
```

**What it does**:
- Watches all workloads (Deployments, Pods, etc.)
- Automatically creates `VulnerabilityReport`, `ConfigAuditReport`, `SecretReport`, `ClusterComplianceReport` CRs
- Exposes Prometheus metrics
- Supports **Policy as Code** via custom Rego or built-in benchmarks

**Best practice values.yaml snippet**:

```yaml
trivy:
  ignoreUnfixed: true
  severity: HIGH,CRITICAL
  dbRepository: ghcr.io/aquasecurity/trivy-db
operator:
  concurrentScanJobsLimit: 5
  scanJobTimeout: 5m
```

### 7.4 Best Practices (Kubernetes Context)

1. **Shift-Left** — Run `trivy image` in **every** CI/CD pipeline (GitHub Actions, GitLab CI, Tekton, Argo Workflows) **before** pushing to registry.
2. **Gate deployments** — Fail pipeline on `CRITICAL` (or `HIGH` in strict environments). Use -`-exit-code 1`.
3. **Ignore unfixed** — `--ignore-unfixed` focuses on **actionable** issues.
4. **Use Trivy Operator** for **runtime/continuous** scanning of running workloads.
5. **Combine with admission controllers** — Kyverno or Gatekeeper + Trivy reports (or Trivy + OPA policies).
6. **SBOM everywhere** — Generate CycloneDX SBOMs and store in artifact registry.
7. **Cache DB** — Mount `/root/.cache` in CI containers for speed.
8. **Custom policies** — Use Rego for organization-specific rules (e.g., "no root images", "no latest tag").
9. **Compliance as Code** — Regularly run `trivy k8s --compliance` in GitOps reconciliation.
10. **Multi-stage scanning** — Image → Manifest → Cluster → Runtime.

###  7.5 Points of Attention / Pitfalls
- **Supply-chain incident (Feb/Mar 2026)**: Malicious v0.69.4 was released via compromised GitHub Actions. **Only use v0.69.3 or later verified releases**. Rotate any secrets if you used affected versions.
- **False positives** — Common with misconfigs on system objects; use `--exclude-kinds` or custom ignore policies.
- **DB freshness** — Trivy auto-updates vulnerability DB; force with `--download-db-only` in air-gapped environments.
- **Resource usage** — Large clusters + Trivy Operator can generate many scan jobs; tune `concurrentScanJobsLimit`.
- **Air-gapped** — Mirror ghcr.io/aquasecurity/trivy-db and trivy-java-db.
- **Secrets scanning** — Very sensitive; false positives possible — review manually for high-severity findings.
- **Kubernetes control-plane scanning** — Requires proper RBAC (ClusterRole with broad `ist` permissions).

## 7.6 References
- Official Docs: https://trivy.dev/docs/latest/
- Kubernetes Scanning: https://trivy.dev/docs/latest/guide/target/kubernetes/
- Trivy Operator: https://github.com/aquasecurity/trivy-operator + https://aquasecurity.github.io/trivy-operator/
- GitHub: https://github.com/aquasecurity/trivy (main) and https://github.com/aquasecurity/trivy-db
- KEPs / Enhancements: Trivy integrates natively with Kubernetes ecosystem (no extra KEP needed).



---

## 8. Scheduling, Scaling & Observability
- **Affinity / Anti-affinity / Topology Spread Constraints for HA.**
- **ResourceQuota, LimitRange, PriorityClass.**
- **HPA + Vertical Pod Autoscaler + Cluster Autoscaler / Karpenter.**
- **Metrics Server, Prometheus + Kube-state-metrics, Loki / Fluent Bit.**

Advice: Use `topologySpreadConstraints` + `podAntiAffinity` for multi-zone resilience.

---

## 9. Best Practices & Platform Engineering

1. **Declarative everything** — store manifests in Git (ArgoCD / Flux).
2. **GitOps** as single source of truth.
3. **Namespace per team/environment**.
4. **Resource requests/limits** mandatory.
5. **Readiness + Liveness + Startup probes**.
6. **Immutable infrastructure** — never kubectl edit in prod.
7. **Multi-tenancy** via namespaces + NetworkPolicy + ResourceQuota.
8. **Observability first** — logs, metrics, traces, SLOs.

**Platform Advice**:
- Use **Cluster API** for infrastructure-as-code clusters.
- **Operators** (Operator SDK) for complex stateful apps.
- **CRDs** for extending Kubernetes API.

---

## 10. Common Pitfalls & Troubleshooting Patterns

|  Pitfall |  Symptom | Fix / Prevention  |
|---|---|---|
| Resource starvation  | Evictions / OOMKills  |  Always set requests/limits |
| Selector overlap  |  Multiple controllers fighting | Unique labels  |
|  etcd bloat | Slow API / high disk  | Compact + backup  |
| Missing NetworkPolicy  | Unexpected traffic | Default-deny  |
|  Secrets in logs |  Security incident |  Never log secrets |
|  Rolling update stuck | Pods in CrashLoop  | Check `progressDeadlineSeconds`  |
|  Trivy false positives | Blocked pipelines  | Use `--ignore-unfixed`, custom Rego policies  |
|  Outdated Trivy/DB | Missed CVEs  | Pin version + cache DB in CI  |
|  Supply-chain compromise | Malicious binary | Verify releases, use only v0.69.3+  |

**Debug commands**:

```bash
kubectl describe pod <name>
kubectl logs <pod> -c <container> --previous
kubectl debug pod/<name> -it --image=busybox
kubectl get events --sort-by=.metadata.creationTimestamp
```

---

## 11. Advanced Topics & Extensibility

- **Custom Resource Definitions (CRDs) + Controllers/Operators**.
- **Admission Webhooks** & **ValidatingAdmissionPolicy**.
- **Gateway API** (successor to Ingress).
- **eBPF** (Cilium) for networking & security.
- **Multi-cluster** (Federation, Karmada, Cluster API).
- **Kubelet** deep dive: CRI, device plugins, dynamic Kubelet config.

**GitHub Exploration Path (github.com/kubernetes/kubernetes)**:
- API types: `api/`
- Core controllers: `pkg/controller/`
- Scheduler: `pkg/scheduler/`
- Client libraries: `staging/src/k8s.io/client-go/`
- Container runtime interfacing, cgroups management, and pod lifecycle management : `pkg/kubelet/`

---

## 11. References & Learning Path
**Official**:
- https://kubernetes.io/docs/home/
- https://kubernetes.io/releases/ (v1.35 changelog)
- https://github.com/kubernetes/kubernetes (master branch)

**Documentation**:
- Architecture: https://kubernetes.io/docs/concepts/architecture/
- Pod Lifecycle: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/
- Network Policies: https://kubernetes.io/docs/concepts/services-networking/network-policies/
- Gateway API: https://gateway-api.sigs.k8s.io/
- Resource Management: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/

**Deep Dives**:
- Kubernetes Enhancement Proposals (KEPs): https://github.com/kubernetes/enhancements
- Source code walkthroughs: `hack/` + `test/e2e/`

**Tools for AI Agents**:
- `kubectl` + `k9s` + `stern` + `kubectx`/`kubens`
- Lens, k6, Trivy, Popeye for linting.

**Trivy-specific**:
- https://trivy.dev/
- Trivy Operator docs
- CKS exam coverage (Trivy is now core for image scanning)

