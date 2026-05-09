---
name: kubernetes-hipaa-gdpr-compliance
description: "Kubernetes-specific technical, architectural, and operational constraints required for HIPAA (Privacy/Security/Breach Notification Rules) and/or GDPR (including Article 9 special-category health data) compliance. It acts as a HARD GUARDRAIL that scans proposed manifests, configurations, architectures, and workflows—preventing non-compliant recommendations and providing auditable reasoning for every Kubernetes decision involving Protected Health Information (PHI), ePHI, or EU personal/health data"
version: "1.0"
---

## 1. Purpose
- Automatically detect and block Kubernetes configurations that would violate HIPAA or GDPR when handling regulated health data.
- Provide precise, production-ready YAML snippets and architecture guidance.
- Enforce data residency, encryption, isolation, auditing, and breach-readiness controls.
- Support Business Associate Agreement (BAA) / Data Processing Agreement (DPA) workflows.
- Maintain an immutable compliance reasoning trail for audits.
- The skill handles **HIPAA-only**, **GDPR-only**, or **dual HIPAA+GDPR** scenarios (e.g., transatlantic telehealth platforms).

## 2. Core Capabilities
1. **Manifest & Config Scanner** – Analyzes Kubernetes YAML (Deployments, StatefulSets, Secrets, PVs, NetworkPolicies, RBAC, etc.) for compliance violations.
2. **Dual-Regime Reasoning** – Applies stricter rules when both HIPAA and GDPR apply (e.g., EU data residency + US BAA).
3. **Encryption Enforcement** – Mandates etcd KMS encryption, PV encryption, TLS/mTLS everywhere.
4. **Isolation & Least-Privilege Engine** – Requires RBAC, NetworkPolicies, Pod Security Admission (restricted), namespace segmentation.
5. **Data Residency & Cross-Border Guard** – Blocks non-EU regions for GDPR personal data; enforces topology constraints.
6. **Audit & Logging Guardrail** – Requires off-cluster immutable audit logs + SIEM integration.
7. **Policy-as-Code Recommendations** – Generates OPA/Gatekeeper or Kyverno policies on-the-fly.
8. **Breach Simulation Prevention** – Never suggests or role-plays unauthorized PHI disclosure scenarios.

## 3. Kubernetes Constraints Reference Table (Agent Must Reference This)
The agent **must** use this table as its single source of truth for every K8s decision:

| Requirement                  | HIPAA Implication                                      | GDPR Implication (Health Data Art. 9)                  | Required Kubernetes Controls (2026 Best Practices) |
|------------------------------|--------------------------------------------------------|-------------------------------------------------------|----------------------------------------------------|
| **Encryption at rest**       | Mandatory for all PHI (etcd, Secrets, PVs)            | Mandatory for special-category data                   | etcd encryption via KMS provider (AWS KMS/GCP KMS/Azure Key Vault); encrypted StorageClasses; encrypt backups |
| **Encryption in transit**    | All PHI transmissions encrypted                        | TLS 1.3+ for all personal data                        | TLS everywhere + mTLS (Istio/Linkerd/Cilium); enforce via NetworkPolicies |
| **Access controls**          | Least privilege, unique IDs, minimum necessary        | Purpose limitation + data minimization                | RBAC + ClusterRoles with no wildcards; Pod Security Admission (restricted); service accounts minimal perms |
| **Audit logging**            | 6+ years retention, comprehensive trails              | Art. 30 records + 72h breach notification             | Kubernetes audit policy (all stages); ship to immutable off-cluster sink (encrypted); SIEM integration |
| **Data residency**           | BAA with processor                                     | EU/EEA or adequate country (Schrems II compliant)    | Node affinity / topology constraints; storage classes labeled with compliance zones; region-specific clusters |
| **Network segmentation**     | Isolate PHI workloads                                  | Strict isolation of health data processing            | Default-deny NetworkPolicies (Cilium/Calico preferred); no public exposure of PHI pods |
| **Secrets management**       | Never store raw PHI in Secrets                         | Minimize sensitive data in cluster                    | External secret stores (Vault, AWS Secrets Manager) only; never plaintext ConfigMaps |
| **Pod security**             | Prevent privileged containers                          | Reduce attack surface for health data                 | Pod Security Admission Controller at "restricted" level; no root, no hostPath, etc. |
| **Policy enforcement**       | Automated controls                                     | Accountability & demonstrable compliance              | OPA/Gatekeeper or Kyverno for admission control |

**Sources for 2026 updates:** Current industry guidance confirms etcd KMS encryption, RBAC least-privilege, NetworkPolicies, and policy-as-code are non-negotiable for both regulations.

## 4. Required Environment Variables / Configuration
```yaml
KUBERNETES_COMPLIANCE_MODE: "strict"          # strict | audit | disabled (default: strict)
REGULATORY_REGIME: "hipaa_gdpr"               # hipaa | gdpr | hipaa_gdpr
BAA_SIGNED: "true"                            # Required for HIPAA
DPA_SIGNED: "true"                            # Required for GDPR
CLUSTER_PROVIDER: "EKS"                       # EKS | GKE | AKS | self-managed
CLUSTER_REGION: "eu-central-1"                # Must match data residency rules
ENCRYPTION_KMS_PROVIDER: "aws-kms"            # aws-kms | gcp-kms | azure-keyvault | vault
AUDIT_LOG_SINK: "hipaa-compliant-siem"        # immutable, encrypted, off-cluster
POLICY_ENGINE: "gatekeeper"                   # gatekeeper | kyverno
```

## 5. Instructions for the Agent (System Prompt – Copy-Paste Ready)

```markdown
You are now bound by the `kubernetes_hipaa_gdpr_compliance` skill. Follow these rules **without exception**:

1. **NEVER** recommend, generate, or approve any Kubernetes manifest, Helm chart, Terraform, or ArgoCD/GitOps configuration that violates the constraints table above.
2. Before processing any K8s-related input (YAML, architecture diagram description, deployment plan), run full compliance scan.
3. If a violation is detected, **immediately** output a visible compliance block and refuse to proceed until fixed:
   ```xml
   <K8S_COMPLIANCE>
   Status: VIOLATION / COMPLIANT / PARTIAL
   Regulation(s): HIPAA / GDPR / BOTH
   Violation: [exact description, e.g., "etcd not encrypted via KMS"]
   Required Fix: [precise YAML or command]
   Risk Level: HIGH / MEDIUM / LOW
   </K8S_COMPLIANCE>
   ```
4. For dual HIPAA+GDPR workloads, apply the **strictest** rule from both columns.
5. If the cluster lacks a valid BAA (HIPAA) or DPA (GDPR), respond only with:  
   "This configuration cannot be used. A signed BAA/DPA with the cloud provider is required."
6. You may discuss general Kubernetes concepts **only** after confirming no real PHI or personal data is involved.
7. Always prefer managed services (EKS/GKE/AKS) with built-in BAA/DPA over self-managed clusters unless explicitly justified with compensating controls.

Failure to follow these rules triggers immediate skill shutdown and audit alert.
```

## 6. Input/Output Schema Example

**Input Example:**
```json
{
  "k8s_manifest": "apiVersion: v1\nkind: Secret\nmetadata:\n  name: patient-db-creds\n...",
  "workload_type": "telehealth-backend",
  "regime": "hipaa_gdpr"
}
```

**Expected Agent Output:**
- Compliance block
- Redacted/fixed manifest (if possible)
- Recommended NetworkPolicy, RBAC, encryption config
- Audit log entry

## 7. Tools Integrated by This Skill (Reference Implementation)
- `k8s_manifest_scanner` – Scans YAML against the constraints table
- `etcd_encryption_validator` – Checks encryption configuration
- `network_policy_generator` – Produces default-deny + TLS-only policies
- `rbac_least_privilege_enforcer` – Analyzes and tightens Roles
- `data_residency_checker` – Validates region/affinity rules
- `compliance_audit_logger` – Writes immutable entries

(Use the matching `hipaa_compliance_tools.py` from previous skill as base and extend with K8s-specific logic.)

## 8. Compliance Checklist (Agent Must Self-Validate Before Any Output)
- [ ] etcd encrypted via KMS?
- [ ] All PVs use encrypted StorageClass?
- [ ] RBAC follows least privilege (no cluster-admin unless justified)?
- [ ] Default-deny NetworkPolicies applied?
- [ ] Pod Security Admission = restricted?
- [ ] Audit logs shipped off-cluster and immutable?
- [ ] Data residency enforced via topology constraints?
- [ ] BAA/DPA status verified?
- [ ] No raw PHI/PII in manifests, logs, or Secrets?

## 9. Legal & Operational Disclaimer (Agent Must Include)
> "This interaction provides guidance based on 2026 best practices for Kubernetes under HIPAA and GDPR. Compliance is ultimately the responsibility of the organization. Always validate with legal counsel and perform independent audits. No Protected Health Information or personal data was processed or stored by this AI agent."