---
name: manage-postgresql-cloudnativepg-k8s
description: Enable an AI agent to autonomously or semi-autonomously deploy, configure, operate, scale, backup, recover, monitor, upgrade, and troubleshoot highly available PostgreSQL clusters on any supported Kubernetes environment using the CloudNativePG (CNPG) operator.
version: "1.2.9"
---

# Postgreql Kubernetes Skill

This skill turns the agent into a "PostgreSQL Kubernetes DBA" that follows declarative GitOps-style workflows, leverages the `Cluster` CRD, the `cnpg` kubectl plugin, CNPG-I plugins for backups, and all native Kubernetes primitives. It is production-ready, follows DevOps and immutable-infrastructure principles, and supports multi-cloud / hybrid / distributed topologies.

## 1. Core Knowledge Base (from full docs exploration)

- **What CloudNativePG is:** Open-source Kubernetes operator (Apache 2.0, CNCF Sandbox) that manages PostgreSQL clusters declaratively. It does not use StatefulSets; it directly manages Pods + PVCs via a custom pod controller for finer control. One primary + optional replicas, automated failover, synchronous replication, WAL archiving, etc.
- **Supported platforms (v1.29):**
  - Kubernetes: 1.33–1.35 (tested down to 1.29).
  - PostgreSQL: 14–18 (default image: `ghcr.io/cloudnative-pg/postgresql:18.3-system-trixie` or via ImageCatalog).
  - Architectures: linux/amd64 + linux/arm64.

- **Key features covered by this skill:**
  - HA with quorum-based failover/switchover.
  - Declarative Postgres config, roles, databases, extensions, tablespaces, schemas, FDWs.
  - Backup/Recovery (volume snapshots + CNPG-I plugins, officially-supported Barman Cloud for object stores).
  - PITR, scheduled/on-demand backups, backup-from-standby.
  - Connection routing (rw/ro services), PgBouncer pooling.

- **Monitoring (Prometheus exporter on port 9187 + PodMonitor).**
  - Rolling updates, major/minor Postgres upgrades, operator upgrades.
  - Replica clusters (distributed topology across clusters/regions).
  - TLS (cert-manager), affinity, resources, storage (PGDATA + WAL + tablespaces), hibernation.
  - kubectl-cnpg plugin for status, report, benchmark, failover, etc.


- **Key features covered by this skill:**
  - HA with quorum-based failover/switchover.
  - Declarative Postgres config, roles, databases, extensions, tablespaces, schemas, FDWs.
  - Backup/Recovery (volume snapshots + CNPG-I plugins, officially-supported Barman Cloud for object stores).
  - PITR, scheduled/on-demand backups, backup-from-standby.
  - Connection routing (rw/ro services), PgBouncer pooling.
  - Monitoring (Prometheus exporter on port 9187 + PodMonitor).
  - Rolling updates, major/minor Postgres upgrades, operator upgrades.
  - Replica clusters (distributed topology across clusters/regions).
  - TLS (cert-manager), affinity, resources, storage (PGDATA + WAL + tablespaces), hibernation.
  - kubectl-cnpg plugin for status, report, benchmark, failover, etc.


## 2. Prerequisites the Agent Must Verify

- Kubernetes cluster with storage class supporting `ReadWriteOnce` (preferably with volume snapshots for backups).
- `kubectl` + `cnpg` plugin installed.
- Operator installed in `cnpg-system` namespace (or custom).
- Secrets for superuser, backups (S3/GCS/Azure/etc.), TLS.
- Network policies/firewalls allow pod-to-pod and external object-store traffic.

## 3. Skill Capabilities (Agent Actions / Tools the Agent Can Execute)


### 3.1 Installation & Setup

**Using the Helm Chart (Recommended for Production & GitOps)**
The CloudNativePG operator can be installed declaratively using the official Helm chart maintained in the cloudnative-pg/charts repository. This method is ideal for GitOps workflows (ArgoCD, Flux, etc.), version-controlled customizations, and repeatable upgrades.


**Prerequisites**

- Helm 3.7+
- Kubernetes ≥ 1.29.0 (matches CloudNativePG v1.29 requirements)
- Cluster-wide RBAC permissions (the chart creates ClusterRoles and ClusterRoleBindings by default)
- A dedicated namespace is strongly recommended (cnpg-system)

**1. Add the Helm Repository**

```bash
helm repo add cnpg https://cloudnative-pg.github.io/charts
helm repo update
```

**2. Install the Operator**
Basic installation (default values):

```bash
helm upgrade --install cnpg \
  --namespace cnpg-system \
  --create-namespace \
  cnpg/cloudnative-pg
```

**Recommended production command** (with common customizations):

```bash
helm upgrade --install cnpg \
  --namespace cnpg-system \
  --create-namespace \
  --set config.clusterWide=true \
  --set monitoring.podMonitorEnabled=true \
  --set crds.create=true \
  cnpg/cloudnative-pg
```

**3. Key Helm Values (from official `values.yaml`)**

The chart exposes many configurable parameters. Here are the most important ones for a v1.29 deployment:

| Key                                 | Type        | Default                               | Description                                                                    |
|-------------------------------------|-------------|---------------------------------------|--------------------------------------------------------------------------------|
| `fullnameOverride`                    | string      | `""`                                  | Override the full name of the deployment (default becomes `cnpg-cloudnative-pg`) |
| `nameOverride`                        | string      | `""`                                  | Override the name prefix                                                       |
| `namespaceOverride`                   | string      | `""`                                  | Override target namespace                                                      |
| `replicaCount`                        | int         | `1`                                     | Number of operator replicas (high availability)                                |
| `image.repository`                    | string      | `ghcr.io/cloudnative-pg/cloudnative-pg` | Operator image                                                                 |
| `image.tag`                           | string      | `""` (uses chart `appVersion`)          | Pin exact operator version (e.g., `1.29.0`)                                      |
| `image.pullPolicy`                    | string      | `IfNotPresent`                          | Image pull policy                                                              |
| `config.clusterWide`                  | bool        | `true`                                  | Watch all namespaces (`false` = namespace-scoped only)                           |
| `config.maxConcurrentReconciles`      | int         | `10`                                    | Maximum concurrent reconciles                                                  |
| `crds.create`                         | bool        | `true`                                  | Automatically install/update CRDs                                              |
| `rbac.create`                         | bool        | `true`                                  | Create ClusterRole + ClusterRoleBinding                                        |
| `rbac.aggregateClusterRoles`          | bool        | `false`                                 | Aggregate into Kubernetes default user-facing roles                            |
| `monitoring.podMonitorEnabled`        | bool        | `false`                                 | Enable PodMonitor for Prometheus Operator                                      |
| `monitoring.grafanaDashboard.create`  | bool        | `false`                                 | Deploy Grafana dashboard ConfigMap                                             |
| `serviceAccount.create`               | bool        | `true`                                  | Create dedicated ServiceAccount                                                |
| `resources`                           | object      | `{}`                              | CPU/memory requests/limits for the operator pod                                |
| `affinity, nodeSelector, tolerations` | object/list | `{}` / `[]`                              | Standard scheduling controls                                                   |


**Full `values.yaml` reference is available in the chart repository:**
https://github.com/cloudnative-pg/charts/blob/main/charts/cloudnative-pg/values.yaml


**4. Example `values.yaml` for Production**

```yaml
fullnameOverride: "cnpg-controller-manager"   # matches manifest naming
config:
  clusterWide: true
  maxConcurrentReconciles: 15
crds:
  create: true
monitoring:
  podMonitorEnabled: true
  grafanaDashboard:
    create: true
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 256Mi
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchExpressions:
        - key: app.kubernetes.io/name
          operator: In
          values: [cloudnative-pg]
      topologyKey: kubernetes.io/hostname
```


Install with custom file:

```bash
helm upgrade --install cnpg \
  --namespace cnpg-system \
  --create-namespace \
  -f values.yaml \
  cnpg/cloudnative-pg
```

**5. Post-Installation Verification**

```bash
# Check deployment
kubectl rollout status deployment -n cnpg-system cnpg-cloudnative-pg

# Verify operator is running
kubectl get pods -n cnpg-system -l app.kubernetes.io/name=cloudnative-pg

# Check CRDs were installed
kubectl get crd clusters.postgresql.cnpg.io
```

You can also use the `cnpg` kubectl plugin:
```bash
kubectl cnpg status --namespace cnpg-system
```


**6. Upgrades via Helm**


```bash
helm repo update
helm upgrade cnpg \
  --namespace cnpg-system \
  cnpg/cloudnative-pg \
  --reuse-values \          # preserves your custom values
  --set image.tag=1.29.x    # or bump chart version
```

The chart handles CRD upgrades automatically when `crds.create: true`.

**7. Uninstallation**

```bash
helm uninstall cnpg --namespace cnpg-system
# CRDs are NOT deleted automatically (safe by design)
```

**Important Notes**
- When installed via Helm, the default deployment name is `cnpg-cloudnative-pg` (different from the YAML manifest’s `cnpg-controller-manager`). Use `fullnameOverride` if you want consistency.
- The chart also supports installing the optional Cluster Helm chart (`cnpg/cluster`) for declarative database provisioning and a cnpg-sandbox chart for quick testing with Prometheus + Grafana (not for production).
- All operator configuration options (from the official docs Operator Configuration section) can be passed via the `config.data` map.


### 3.2 Create / Manage a PostgreSQL Cluster (Core `Cluster `CRD)

Agent generates and applies a `Cluster` resource. Minimal example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: prod-db
spec:
  instances: 3
  imageName: ghcr.io/cloudnative-pg/postgresql:17.4  # or use ImageCatalog
  storage:
    size: 100Gi
    storageClass: premium-rwo
  walStorage:
    size: 20Gi
  postgresql:
    parameters:
      max_connections: "300"
      shared_buffers: "2GB"
    pg_hba:
      - host all all 0.0.0.0/0 scram-sha-256
  backup:
    barmanObjectStore:   # or volumeSnapshot
      destinationPath: s3://my-bucket/backups/
      s3Credentials:
        accessKeyId:
          name: aws-creds
          key: ACCESS_KEY
        secretAccessKey:
          name: aws-creds
          key: SECRET_KEY
    retentionPolicy: "30d"
  monitoring:
    enablePodMonitor: true
```

Agent can:
- Scale instances up/down.
- Add tablespaces, managed databases/roles/extensions.
- Enable synchronous replication (`minSyncReplicas`, `maxSyncReplicas`).
- Configure replica clusters for geo-distribution.

### 3.3 Backup & Recovery (CNPG-I + Barman Cloud or Snapshots)

- Create `ScheduledBackup` or on-demand `Backup` CR.
- Recovery: Use `.spec.bootstrap.recovery` with `source` pointing to backup or external cluster.
- PITR supported (timestamp, transaction ID, named restore point).
- Agent can trigger backup-from-standby to reduce primary load.

### 3.4 Operations & Maintenance
- Failover / Switchover: `kubectl cnpg failover prod-db` or declarative via `FailoverQuorum`.
- Rolling updates: Change `imageName` → operator handles one pod at a time + optional supervised switchover.
- Major Postgres upgrade: Change image to new major version → offline in-place upgrade (new base backup required after).
- Connection pooling: Deploy `Pooler` CR (PgBouncer) attached to `rw`/`ro` services.
- Monitoring: Agent can deploy Prometheus/Grafana stack and interpret metrics (exporter auto-exposes ~100 Postgres + CNPG metrics).
- Benchmarking: `kubectl cnpg benchmark prod-db` (pgbench + fio).
- Hibernation / Fencing: Declarative via CR fields.
- Import existing DB: Logical replication or physical import via `bootstrap.initdb.import`.

## 3.5 1.29-Specific Enhancements
- `https://cloudnative-pg.io/releases/cloudnative-pg-1-29.0-released/`

**A. Dynamic Network Security (Pod Selectors in pg_hba)**

- New Capability: The agent should prefer `podSelectorRefs` over static CIDR ranges in `pg_hba` rules. This allows the operator to dynamically resolve the ephemeral IP addresses of client pods based on labels.

- Example Pattern:
```yaml
postgresql:
  pg_hba:
    - hostssl all all all cert
      podSelectorRefs:
        - name: app-frontend-selector # References a label selector for client pods
```

**B. Enterprise Identity (Shared ServiceAccounts)**

- New Capability: Both `Cluster` and `Pooler` (PgBouncer) now support the `serviceAccountName` field.
- Agent Action: When integrating with Cloud IAM (AWS IRSA, GCP Workload Identity, Azure AD), the agent should reference a pre-existing, IAM-annotated ServiceAccount instead of letting the operator create a default one.  

Example Pattern:
```yaml
spec:
  serviceAccountName: "postgres-iam-sa"
```

**C. PostgreSQL Extension Ecosystem (Image Volumes)**

- New Capability: The agent can now manage extensions as first-class objects using OCI-compliant "Extension Images" via the `postgresql.extensions` stanza.
- Requirements: Requires Kubernetes 1.35+ (or 1.33+ with the `ImageVolume` feature gate enabled).
- Agent Workflow:
  - void building custom "fat" Docker images for extensions like `pgvector` or `PostGIS`.
  - Use the `image` field to pull extension binaries dynamically.
  - Use the per-extension `env` field to configure specific modules.

Example Pattern:
```yaml
postgresql:
  extensions:
    - name: pgvector
      image: "ghcr.io/cloudnative-pg/postgresql-extensions/pgvector:0.7.0"
      env:
        - name: VECTOR_MAX_DIMENSION
          value: "2000"
```


**D. Granular Backup Lifecycle Tracking**

- New Status Fields: `reconciliationStartedAt` and `reconciliationTerminatedAt` in the `Backup` CRD.
- Agent Action: During troubleshooting, the agent should parse these timestamps to determine if a delay is caused by the operator's reconciliation logic or the underlying backup tool (e.g., Barman).

**E. Advanced PgBouncer TLS Security*
- New Capability: Use t`ls.minProtocolVersion`, `tls.maxProtocolVersion`, and `tls.cipherSuites` within the `Pooler` spec for strict compliance (e.g., FIPS or PCI-DSS).


### 3.5 Troubleshooting & Observability

- `kubectl cnpg status prod-db --verbose`
- `kubectl cnpg report prod-db` → generates ZIP with logs, configs, PVC info.
- Check conditions in `Cluster.status`.
- Logs: JSON-formatted, accessible via `kubectl logs`.


## 4. Agent Workflow Patterns (Prompt Templates the Agent Should Follow)
When user asks e.g. “Deploy a 3-node HA Postgres 17 cluster with daily backups to S3”:

- Verify prerequisites (K8s version, storage class, credentials).
- Generate `Cluster` YAML (use specific image tag/digest, not `latest`).
- Apply + wait for `Ready` condition.
- Create services / Pooler if needed.
- Set up backup + monitoring.
- Output connection string from generated Secret.
- Provide `kubectl cnpg` commands for day-2 ops.

## 5. Safety & Best Practices Enforced by This Skill

- Never use `latest` image tags in production.
- Always use specific PostgreSQL tags or ImageCatalog.
- Prefer volume snapshots + object-store backups for RPO/RTO < 5 min.
- Enable PodAntiAffinity by default.
- Superuser access disabled by default (`enableSuperuserAccess:` false).
- Read release notes before any upgrade.
- Use `cnpg.io/cluster` label (deprecated `postgresql` label removed).


## 6. Integration Points for the AI Agent (`Disguard for the moment`)
- Can call Kubernetes API directly (create/update CRs).
- Can execute kubectl cnpg plugin commands.
- Can parse Cluster.status and conditions.
- Can generate YAML from natural language requirements.
- Can troubleshoot by analyzing events, logs, and metrics.


## Tips
- Extension Precedence: If the agent defines the same environment variable in `spec.env` and in an extension's `env` stanza, the extension-level variable takes precedence.
- ServiceAccount Sharing: Remind users that if they use a shared `ServiceAccount`, they are responsible for ensuring it has the necessary permissions (RBAC) that the operator normally grants to its auto-generated accounts.

**Documentation**
- https://cloudnative-pg.io/docs/1.29/