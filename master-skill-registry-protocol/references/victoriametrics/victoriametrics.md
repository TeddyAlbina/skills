---
name: victoriametrics
description: >
  Explains the differences between the open source (community) version of VictoriaMetrics and the Enterprise version.
---

# Enterprise-only features
Enterprise includes everything above plus these additions:

**The core of VictoriaMetrics (metrics, logs, traces) is completely open source and free.**  

Here’s a clear, up-to-date breakdown of the differences (as of May 2026, based on the official documentation):

### 1. What you get in both Open Source (Community) and Enterprise
- All core functionality (single-node + cluster mode for VictoriaMetrics, VictoriaLogs, VictoriaTraces)
- Prometheus/PromQL compatibility, MetricsQL, Grafana support
- High performance, excellent compression, cardinality handling
- Kubernetes Operator, Helm charts, `vmagent`, `vmalert`, etc.
- Basic security (TLS/HTTPS, basic auth)
- Backup/restore CLI (`vmbackup` / `vmrestore`)
- All the features that already make VictoriaMetrics simpler and more efficient than your current Prometheus + Thanos + Loki + Tempo stack

**No license needed** — you can run the open-source version in production forever at zero cost.

### 2. Enterprise-only features (what you pay for)
Enterprise includes everything above **plus** these additions:

| Category              | Enterprise-only / Enhanced Features                                                                 |
|-----------------------|-----------------------------------------------------------------------------------------------------|
| **Releases & Support**| • Long-term support (LTS) releases with extended bug/security fixes<br>• First-class support from the core development team<br>• Prioritized feature requests<br>• 3-day SLA for security vulnerabilities (CVEs) |
| **Storage & Cost**    | • **Downsampling** (global, per-label, or per-tenant) – saves disk space and speeds up historical queries<br>• **Multiple / per-tenant data retention** – different retention policies for different datasets |
| **Operations**        | • **Backup Manager** (`vmbackupmanager`) – automated multi-retention backups<br>• Automatic `vmstorage` node discovery (no restart needed when scaling cluster)<br>• Advanced per-tenant statistics & query execution stats |
| **Security & Auth**   | • mTLS for **all** components and between cluster components<br>• Advanced `vmauth` (IP filtering, mTLS-based routing)<br>• SSO / LDAP / OpenID Connect / JWT authentication<br>• Automatic TLS certificate issuance<br>• FIPS 140-3 compliant builds |
| **Integrations**      | • Kafka consumer/producer in `vmagent`<br>• Google Pub/Sub consumer/producer in `vmagent`<br>• Read alerting/recording rules from S3/GCS in `vmalert` |
| **Alerting**          | • Multi-tenancy support in `vmalert`<br>• Per-tenant alert routing |
| **Advanced Analytics**| • **Anomaly Detection** service (`vmanomaly`) – automates complex alerting with ML models |
| **Monitoring of Monitoring** | • “Monitoring of Monitoring” (MoM) – tracks health of your VictoriaMetrics setup itself |

### 3. VictoriaLogs Enterprise
It gets a smaller subset of the above (mainly support, LTS, mTLS, security compliance).

### 4. Pricing & Licensing
- **Open Source** → Free forever (Apache 2.0)
- **Enterprise** → Commercial license (contact VictoriaMetrics sales for quote). Usually sold as annual subscription that includes support + the extra features.
- You can test Enterprise features with a **free 2-month evaluation license**.

### Bottom line for your Kubernetes setup
- If you’re happy with the open-source version’s performance, security, and operations → **stay on open source** (most users do).
- You only need Enterprise if you want:
  - Downsampling + per-tenant retention (big storage/cost savings at scale)
  - Automated backups
  - Advanced mTLS/SSO/security
  - Anomaly detection
  - Official LTS + direct support from the core team
  
  
## References open-source (community) version’s
- https://docs.victoriametrics.com/victoriametrics/quick-start/
- https://docs.victoriametrics.com/victoriametrics/integrations/
- https://docs.victoriametrics.com/victoriametrics/
- https://docs.victoriametrics.com/victorialogs/quickstart/
- https://docs.victoriametrics.com/victorialogs/keyconcepts/
- https://docs.victoriametrics.com/victorialogs/
- https://docs.victoriametrics.com/victoriatraces/#quick-start
- https://docs.victoriametrics.com/victoriatraces/keyconcepts/
- https://docs.victoriametrics.com/victoriatraces/
- https://docs.victoriametrics.com/operator/
- https://docs.victoriametrics.com/guides/
- https://docs.victoriametrics.com/opentelemetry/
- https://docs.victoriametrics.com/helm/