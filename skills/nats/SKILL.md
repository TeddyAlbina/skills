---
name: nats
description: >
  NATS is a simple, secure, and high-performance open source messaging system for cloud native applications, IoT, and microservices. This skill covers deploying and operating NATS Server, JetStream persistence, clustering, leaf nodes, and gateways on Kubernetes and bare metal. It provides configuration patterns, security hardening, troubleshooting, and operational guidance for the NATS ecosystem. Activate for NATS server configuration, JetStream streams/consumers, Helm chart deployment, clustering, security setup, or performance tuning.
version: "1.0"
---

# NATS

## When to Use This Skill

Invoke this skill when the user mentions or asks about:

- **Deploying NATS** on Kubernetes, Docker, VMs, or bare metal.
- **Configuring NATS Server** (`nats-server`, `nats.conf`, CLI flags).
- **JetStream** (streams, consumers, Key-Value store, Object Store, persistence, replication).
- **Core NATS** (pub/sub, request/reply, queue groups, subject hierarchies).
- **Clustering / High Availability** (NATS clusters, super-clusters, leaf nodes, gateways).
- **Security** (TLS, JWT, NKEY, username/password, auth callout, authorization).
- **Helm charts** (`nats/nats`, `nats/nack`, `nats/surveyor`).
- **Monitoring / Observability** (Prometheus metrics, NATS Surveyor, server statistics).
- **Troubleshooting** (slow consumers, connection issues, stream lag, RAFT quorum).
- **Client SDKs** (Go, Rust, Python, Node.js, C#, Java, etc.) — primarily from an infrastructure/operations perspective.

## Core Concepts

### NATS Server (nats-server)
A single, lightweight binary (< 20 MB) with no external dependencies. It supports:

- **Core NATS**: At-most-once pub/sub messaging with millions of messages per second.
- **Request/Reply**: Synchronous or asynchronous RPC over subjects.
- **Queue Groups**: Load-balance message delivery across a group of subscribers.
- **Subject Hierarchies**: Dot-separated subjects (e.g., `orders.us.east`) with wildcard support (`*`, `>`).

### JetStream (Persistence Layer)
Built into `nats-server`. Provides at-least-once and exactly-once delivery, temporal decoupling, and distributed storage.

| Feature | Description |
|---------|-------------|
| **Streams** | Named persistent message logs with retention policies and limits. |
| **Consumers** | Views on a stream. Push (fast, ordered) or Pull (scalable, acked, batched). |
| **Retention Policies** | `limits` (default replay), `work queue` (exactly-once consumption), `interest` (retain while consumers exist). |
| **Discard Policies** | `discard old` (delete oldest) or `discard new` (reject new messages) when limits are reached. |
| **Replication (R)** | R=1 (fast, no HA) to R=5 (tolerate 2 server loss). R=3 is the recommended balance. |
| **Key-Value Store** | Atomic operations, watchers, versioning, TTL. Built on top of JetStream. |
| **Object Store** | Chunked file storage with versioning. Built on top of JetStream. |
| **Mirroring / Sourcing** | Replicate streams across JetStream domains for DR or aggregation. |

**Consistency Model**: JetStream uses a NATS-optimized RAFT algorithm. Writes are linearizable; reads are effectively serializable. For the strongest read consistency, send get requests to the stream leader.

### Topologies

| Topology | Use Case |
|----------|----------|
| **Single Server** | Dev/test, edge devices. |
| **Cluster** | HA production. 3+ nodes with RAFT for JetStream metadata and streams. |
| **Leaf Node** | Extend a cluster into a remote VPC, edge location, or K8s namespace. Transparent proxy. |
| **Gateway** | Connect clusters across regions/clouds. Filters traffic, enables geo-replication and DR. |
| **Super-Cluster** | Multiple clusters connected via gateways forming a global mesh. |

## Deploying on Kubernetes

### Quick Start with Helm

The official Helm charts are maintained at [nats-io/k8s](https://github.com/nats-io/k8s). See the local reference: [`references/kubernetes/README.md`](references/kubernetes/README.md).

```sh
helm repo add nats https://nats-io.github.io/k8s/helm/charts/
helm repo update
helm install my-nats nats/nats
```

### Primary Charts

| Chart | Purpose | Reference |
|-------|---------|-----------|
| **`nats`** | NATS server (core + JetStream) | [`references/kubernetes/CLAUDE.md`](references/kubernetes/CLAUDE.md) |
| **`nack`** | JetStream Controller (CRDs for K8s) | [`references/kubernetes/CLAUDE.md`](references/kubernetes/CLAUDE.md) |
| **`surveyor`** | Prometheus monitoring for NATS | [`references/kubernetes/README.md`](references/kubernetes/README.md) |

### Chart Architecture (nats)

The `nats` chart uses a unique **loadMergePatch** pattern:

1. **`templates/`** are thin wrappers calling `nats.loadMergePatch`.
2. **`files/`** contains the actual YAML definitions, loaded via `.Files.Get`.
3. Users can customize almost any resource via `merge: {}` (deep merge) and `patch: []` (RFC 6902 JSON Patch) in `values.yaml`.

**Key values structure:**

- `config.*`: NATS server config (maps to `nats.conf` sections).
  - Sub-keys: `nats`, `cluster`, `jetstream`, `leafnodes`, `websocket`, `mqtt`, `gateway`, `monitor`, `profiling`, `resolver`.
  - Each protocol has `enabled`, `port`, `tls`.
  - Each section supports `merge: {}` and `patch: []`.
- `container.*`: Server container spec (image, ports, env, resources).
- `reloader.*`: Config reloader sidecar.
- `promExporter.*`: Prometheus exporter sidecar.
- `statefulSet.*`, `podTemplate.*`, `headlessService.*`, `configMap.*`: K8s resource customization.
- `natsBox.*`: NATS Box deployment (CLI tools with pre-configured contexts).
- `extraResources`: Arbitrary additional K8s resources.

**Config merge special syntax:**
- Strings wrapped in `<< >>` are unquoted (for NATS size units like `1GB` or env vars like `$TOKEN`).
- Keys ending in `$include` become NATS `include` directives.

### NACK (JetStream Controller)

NACK allows managing JetStream resources via Kubernetes CRDs (`Stream`, `Consumer`, `Account`, etc.).

- CRDs are in `crds/crds.yml` and auto-updated.
- Helper prefix in templates: `jsc.*`.
- Has `useLegacyNames` toggle for K8s label compatibility.

### Local Development / Validation

Render and lint locally without installing:

```sh
# Render templates
helm template my-nats helm/charts/nats
helm template my-nats helm/charts/nats -f custom.yaml

# Lint with chart-testing
ct lint --all --chart-dirs helm/charts \
  --excluded-charts nats-account-server,nats-kafka,nats-operator,surveyor \
  --validate-maintainers=false

# Run Go template tests
cd helm/charts/nats/test && go test
```

See full commands in [`references/kubernetes/CLAUDE.md`](references/kubernetes/CLAUDE.md).

## Server Configuration

### Minimal nats.conf

```hcl
# Single node with JetStream
jetstream {
  store_dir: "/data/jetstream"
}
```

### Cluster with JetStream

```hcl
server_name: nats-1
jetstream {
  store_dir: "/data/jetstream"
}
cluster {
  name: my-cluster
  listen: 0.0.0.0:6222
  routes: [
    nats-route://nats-2:6222
    nats-route://nats-3:6222
  ]
}
```

### Protocols and Ports

| Protocol | Default Port | Config Section | Notes |
|----------|-------------|----------------|-------|
| NATS Client | 4222 | `nats` | Core TCP port. |
| Cluster Routes | 6222 | `cluster` | Inter-server routing. |
| Gateway | 7222 | `gateway` | Inter-cluster / super-cluster. |
| Leaf Node | 7422 | `leafnodes` | Accept leaf node connections. |
| WebSocket | 8080 | `websocket` | WebSocket support. |
| MQTT | 1883 | `mqtt` | MQTT 3.1.1 bridge. |
| Monitor / HTTP | 8222 | `monitor` | Server stats, health, debug vars. |
| Profiling | - | `profiling` | Go pprof endpoint. |

## Security

NATS provides multi-level security with account isolation.

### Authentication Methods

| Method | Description | Reference |
|--------|-------------|-----------|
| **Token** | Global shared token. | [docs](https://docs.nats.io/running-a-nats-service/configuration/securing_nats/auth_intro/tokens) |
| **Username/Password** | Plain text or bcrypt-hashed. | [docs](https://docs.nats.io/running-a-nats-service/configuration/securing_nats/auth_intro/username_password) |
| **TLS (mTLS)** | Client certificate authentication. | [docs](https://docs.nats.io/running-a-nats-service/configuration/securing_nats/auth_intro/tls_mutual_auth) |
| **NKEY** | Ed25519 public key with server challenge. | [docs](https://docs.nats.io/running-a-nats-service/configuration/securing_nats/auth_intro/nkey_auth) |
| **Decentralized JWT** | Zero-trust with operators, accounts, and users. | [docs](https://docs.nats.io/running-a-nats-service/configuration/securing_nats/auth_intro/jwt) |

### Authorization

- The `authorization` block configures both auth and per-user permissions.
- Each user can have `permissions` restricting publish/subscribe subjects.
- Accounts provide subject namespace isolation; cross-account traffic uses `exports` and `imports`.

### TLS

Almost every protocol section (`cluster`, `leafnodes`, `websocket`, `mqtt`, `gateway`, `monitor`) supports `tls`:

```hcl
cluster {
  port: 6222
  tls {
    cert_file: "/certs/server.pem"
    key_file: "/certs/server.key"
    ca_file: "/certs/ca.pem"
  }
}
```

In the Helm chart, TLS is configured via `config.*.tls.enabled` and `secretName`.

## Operations

### Monitoring

- **HTTP Monitor** (`monitor` port 8222): `/varz`, `/connz`, `/routez`, `/gatewayz`, `/leafz`, `/jsz`, `/healthz`, `/subsz`.
- **Prometheus Exporter**: Sidecar in Helm chart (`promExporter.enabled: true`).
- **NATS Surveyor**: Standalone tool for cluster-wide metrics. See `surveyor` Helm chart.
- **Server Statistics**: Via `nats server info`, `nats server report`, `nats server watch` (NATS CLI).

### JetStream Operations

```sh
# Check stream info
nats stream info ORDERS

# Check consumer info
nats consumer info ORDERS NEW

# Server report for JetStream
nats server report jetstream

# Evacuate a server (drain streams/consumers before maintenance)
nats server evacuate <server-name>
```

### Durability and fsync

JetStream file stores flush to the OS synchronously but do not `fsync` on every write by default. The `sync_interval` (default 2 minutes) controls how often `fsync` runs.

- **Default**: Balanced performance and risk. Suitable for multi-AZ deployments with R=3.
- **`sync_interval: always`**: Strongest durability, slowest performance. Use for critical financial or compliance data.
- **Mitigation**: Lower `sync_interval` or use placement tags to route critical streams to a dedicated high-durability cluster.

See [JetStream sync documentation](https://docs.nats.io/nats-concepts/jetstream) for failure scenarios.

### Troubleshooting

| Symptom | Likely Cause | Action |
|---------|--------------|--------|
| **Slow Consumers** | Client not reading fast enough; server is buffering. | Scale consumers or increase buffer. Check `slow_consumer_threshold`. |
| **JetStream publish timeout** | Stream leader unreachable or quorum lost. | Check cluster health, RAFT status (`nats server report raft`), network partitions. |
| **Message duplication** | Network blip, consumer ack lost, or publisher retry. | Use exactly-once semantics (dedup headers, double-ack consumers). |
| **Stream lag / high redelivery** | Slow processing, consumer offline, or nack loop. | Inspect consumer stats, check app logs, scale pull consumers. |
| **Connection refused** | Wrong port, TLS required but not used, auth failure. | Verify client URL, `tls` settings, and `authorization` block. |
| **Cluster not forming** | Route URLs misconfigured, firewall blocking gossip, or server_name duplicates. | Verify `cluster.routes`, `server_name` uniqueness, and port reachability. |
| **Disk full / stream limits** | Retention policy or max bytes/message count reached. | Increase limits, change discard policy, or age out old messages. |

### Scaling

- **Horizontal**: Add servers to the cluster. JetStream will auto-rebalance RAFT groups over time. For immediate effect, evacuate and restart.
- **Vertical**: Increase CPU/disk for JetStream nodes. SSD/NVMe is strongly recommended for file stores.
- **Placement Tags**: Pin streams to specific servers using `server_tags` and stream `placement` for topology-aware durability.

## Developer Quick Reference

### NATS CLI (nats)

The `nats` CLI is the primary operational tool.

```sh
# Pub/Sub
nats pub orders.new "hello"
nats sub orders.new

# Request/Reply
nats req orders.service "request" --wait 5s

# JetStream
nats stream add ORDERS --subjects "orders.*" --storage file --replicas 3
nats consumer add ORDERS PROCESSOR --pull --ack explicit
nats consumer next ORDERS PROCESSOR

# KV
nats kv add CONFIG
nats kv put CONFIG key value
nats kv get CONFIG key
```

### SDKs

Official clients exist for Go, Rust, Python, Node.js, C#, Java, C, Elixir, and more. See [NATS Clients](https://docs.nats.io/using-nats/developer).

## References

### Official Documentation
- **Main Docs**: https://docs.nats.io/
- **JetStream**: https://docs.nats.io/nats-concepts/jetstream
- **Security / Auth**: https://docs.nats.io/running-a-nats-service/configuration/securing_nats/auth_intro
- **Server Config**: https://docs.nats.io/running-a-nats-service/configuration
- **NATS by Example**: https://natsbyexample.com

### Local References
- **K8s Helm Charts README**: [`references/kubernetes/README.md`](references/kubernetes/README.md)
- **K8s Chart Development (CLAUDE.md)**: [`references/kubernetes/CLAUDE.md`](references/kubernetes/CLAUDE.md) — Build commands, architecture, values structure, CI workflows, and conventions.
- **Dependencies**: [`references/kubernetes/dependencies.md`](references/kubernetes/dependencies.md)
- **Helm Chart Dir**: [`references/kubernetes/helm/`](references/kubernetes/helm/)
- **Kine + NATS Example**: [`references/kubernetes/kine-nats/`](references/kubernetes/kine-nats/)

### External Projects
- **NATS Server**: https://github.com/nats-io/nats-server
- **K8s Helm Charts**: https://github.com/nats-io/k8s
- **NACK (JetStream Controller)**: https://github.com/nats-io/nack
- **NATS CLI**: https://github.com/nats-io/natscli
- **NATS Surveyor**: https://github.com/nats-io/nats-surveyor
