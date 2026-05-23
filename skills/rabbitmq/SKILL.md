---
name: rabbitmq
description: Comprehensive RabbitMQ guidance for message brokering, AMQP protocols, clustering, Kubernetes deployment, and operations. Covers installation, configuration, monitoring, upgrade, and production deployment.
version: "1.0"
---

# RabbitMQ Skill

Use this skill when working with RabbitMQ for message brokering, AMQP protocols, clustering, Kubernetes operators, or production deployment.

## Description

This skill provides comprehensive guidance on RabbitMQ — an open-source message broker implementing the AMQP, AMQP 1.0, MQTT, STOMP, HTTP, and WebSocket protocols. It covers the full lifecycle: from initial setup and development tutorials through clustering, monitoring, production deployment, and upgrades.

## When to Use

- Installing or configuring RabbitMQ on any platform
- Building messaging applications using AMQP 0-9-1 or AMQP 1.0
- Setting up RabbitMQ clusters for high availability
- Deploying RabbitMQ on Kubernetes using operators
- Monitoring RabbitMQ with Prometheus/Grafana
- Performing rolling upgrades or blue-green deployments
- Troubleshooting connections, queues, or message routing
- Managing users, virtual hosts, and permissions
- Configuring exchanges, bindings, and queue behaviors
- Implementing publisher confirms and consumer prefetch
- Working with quorum queues, streams, or classic queues
- Setting up federation, shovels, or cross-cluster replication

## Linked Documentation

### [release-information/](release-information/index.md)
Release lifecycle and support status for all RabbitMQ versions. Contains the version support table showing which releases have commercial or community support, plus end-of-life dates. **Use when:** checking which RabbitMQ version is currently supported, planning upgrades, or determining long-term support eligibility.

### [version-4.3/](version-4.3/index.md)
**Primary documentation for RabbitMQ 4.x** — the current major version. Contains ~140 markdown files covering every aspect of RabbitMQ:

#### Core Concepts & Configuration
- [configure.md](version-4.3/configure.md) — Configuration file formats (`rabbitmq.conf`, `advanced.config`), environment variables, kernel limits, configuration encryption
- [production-checklist.md](version-4.3/production-checklist.md) — Production deployment checklist covering storage, networking, security, clustering, and application practices
- [upgrade.md](version-4.3/upgrade.md) — Upgrade strategies: rolling (in-place), blue-green deployment, and grow-then-shrink patterns

#### Clustering & Networking
- [clustering.md](version-4.3/clustering.md) — Cluster formation, node names, Erlang cookie authentication, replica placement, node restarts
- [cluster-formation.md](version-4.3/cluster-formation.md) — Peer discovery and automatic cluster formation
- [networking.md](version-4.3/networking.md) — Network configuration, connection limits, keepalive, TCP settings
- [ssl.md](version-4.3/ssl/index.md) — TLS/SSL configuration for inter-node and client connections

#### Queues & Messaging
- [queues.md](version-4.3/queues.md) — Queue types, properties, and behaviors
- [quorum-queues.md](version-4.3/quorum-queues.md) — Quorum queues (replicated, crash-safe)
- [streams.md](version-4.3/streams.md) — RabbitMQ Streams for high-throughput, log-based messaging
- [classic-queues.md](version-4.3/classic-queues.md) — Classic queue implementation
- [exchanges.md](version-4.3/exchanges.md) — Exchange types: direct, fanout, topic, headers
- [confirms.md](version-4.3/confirms.md) — Publisher confirms and acknowledgments
- [consumers.md](version-4.3/consumers.md) — Consumer lifecycle, cancel notifications, prefetch

#### Protocols
- [amqp.md](version-4.3/amqp.md) — AMQP 0-9-1 protocol reference
- [specification.md](version-4.3/specification.md) — AMQP conformance and compatibility
- [mqtt.md](version-4.3/mqtt.md) — MQTT protocol support
- [stomp.md](version-4.3/stomp.md) — STOMP protocol support
- [stream.md](version-4.3/stream.md) — Stream protocol (HTTP-based)

#### Operations & Management
- [monitoring/index.md](version-4.3/monitoring/index.md) — Monitoring infrastructure with Prometheus/Grafana, CLI observer, health checks
- [management/index.md](version-4.3/management/index.md) — Management plugin HTTP API and UI
- [logging.md](version-4.3/logging.md) — Log configuration and management
- [access-control.md](version-4.3/access-control.md) — User authentication and permissions
- [vhosts.md](version-4.3/vhosts.md) — Virtual hosts configuration
- [parameters.md](version-4.3/parameters.md) — Runtime parameters and policies
- [policies.md](version-4.3/policies.md) — Stream and queue policy management

#### Reliability & Distribution
- [reliability.md](version-4.3/reliability.md) — Message durability, publisher confirms, consumer acknowledgments
- [federation.md](version-4.3/federation.md) — Cross-cluster federation
- [shovel.md](version-4.3/shovel.md) — Message shovel between brokers
- [partitions.md](version-4.3/partitions.md) — Handling network partitions
- [backup.md](version-4.3/backup.md) — Backup and restore procedures

### [tutorials/](tutorials/index.md)
Hands-on tutorials for learning RabbitMQ by building messaging applications. Three tutorial groups:

1. **AMQP 1.0 Queue Tutorials** — Modern protocol tutorials (Java, C#, Go): Hello World, Work Queues, Publish/Subscribe, Routing, Topics, RPC

2. **AMQP 0-9-1 Queue Tutorials** — Classic protocol tutorials with implementations in Python, Java, Kotlin, Ruby, PHP, C#, JavaScript, Go, Elixir, Swift, Spring AMQP. Covers same patterns as AMQP 1.0 group plus Publisher Confirms

3. **Stream Tutorials** — RabbitMQ Streams tutorials (Java, C#, Go, Python, Rust, Node.js): Hello World, Offset Tracking

**Use when:** learning RabbitMQ concepts, getting started with a new client library, or following the "Hello World" → Work Queues → Publish/Subscribe → Routing → Topics → RPC learning path.

### [kubernetes/operator/](kubernetes/operator/operator-overview.md)
**RabbitMQ on Kubernetes** — Two Kubernetes operators maintained by the RabbitMQ team:

#### Cluster Kubernetes Operator
- [quickstart-operator.md](kubernetes/operator/quickstart-operator.md) — Quick start guide
- [install-operator.md](kubernetes/operator/install-operator.md) — Installation
- [using-operator/](kubernetes/operator/using-operator/index.md) — Usage guide
- [operator-monitoring.md](kubernetes/operator/operator-monitoring.md) — Monitoring on Kubernetes
- [troubleshooting-operator.md](kubernetes/operator/troubleshooting-operator.md) — Debugging

#### Messaging Topology Operator
- [install-topology-operator.md](kubernetes/operator/install-topology-operator.md) — Installation
- [using-topology-operator.md](kubernetes/operator/using-topology-operator.md) — Managing queues, exchanges, bindings declaratively
- [tls-topology-operator.md](kubernetes/operator/tls-topology-operator.md) — TLS configuration

**Use when:** deploying RabbitMQ clusters on Kubernetes, managing messaging topology via Kubernetes resources, or setting up monitoring with Prometheus on Kubernetes.

## Key Topics Quick Reference

| Task | Documentation |
|------|-------------|
| Install RabbitMQ | [version-4.3/download.md](version-4.3/download.md) |
| Configure broker | [version-4.3/configure.md](version-4.3/configure.md) |
| Build messaging app | [tutorials/](tutorials/index.md) |
| Cluster setup | [version-4.3/clustering.md](version-4.3/clustering.md) |
| Kubernetes deploy | [kubernetes/operator/](kubernetes/operator/operator-overview.md) |
| Monitor production | [version-4.3/monitoring/](version-4.3/monitoring/index.md) |
| Upgrade safely | [version-4.3/upgrade.md](version-4.3/upgrade.md) |
| User management | [version-4.3/access-control.md](version-4.3/access-control.md) |

## Version Compatibility

- This skill targets **RabbitMQ 4.x** (current stable)
- Tutorials support both AMQP 0-9-1 and AMQP 1.0
- Kubernetes operators support a range of K8s versions — check operator README for details